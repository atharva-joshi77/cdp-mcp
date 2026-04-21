-- =====================================================================
-- RESUMABLE BATCH Retention Script for `segment_stats_def`
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. CONFIGURATION
-- ---------------------------------------------------------------------
SET SQL_SAFE_UPDATES      = 0;
SET @RECORDS_TO_KEEP      = 3;
SET @BATCH_SIZE           = 500;
SET @MAX_GROUPS_PER_RUN   = 5000;
SET @SLEEP_BETWEEN_BATCHES = 0.3;
SET @RESET_CURSOR         = 0; 

-- ---------------------------------------------------------------------
-- 2. PERSISTENT CHECKPOINT
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS segment_stats_def_retention_cursor (
    id                 TINYINT   NOT NULL PRIMARY KEY,
    last_audience_id   BIGINT    NULL,
    last_segment_id    BIGINT    NULL,
    groups_done_total  BIGINT    NOT NULL DEFAULT 0,
    rows_deleted_total BIGINT    NOT NULL DEFAULT 0,
    updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                                           ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO segment_stats_def_retention_cursor(id) VALUES (1);

-- Optional hard reset
UPDATE segment_stats_def_retention_cursor
   SET last_audience_id = NULL,
       last_segment_id  = NULL,
       groups_done_total = 0,
       rows_deleted_total = 0
 WHERE id = 1 AND @RESET_CURSOR = 1;

SELECT 'CURRENT CHECKPOINT' AS status, last_audience_id, last_segment_id,
       groups_done_total, rows_deleted_total, updated_at
  FROM segment_stats_def_retention_cursor WHERE id = 1;

-- ---------------------------------------------------------------------
-- 3. BUILD THIS-RUN WORK LIST
-- ---------------------------------------------------------------------
SELECT last_audience_id, last_segment_id
  INTO @cur_aud, @cur_seg
  FROM segment_stats_def_retention_cursor WHERE id = 1;

DROP TEMPORARY TABLE IF EXISTS ids_to_delete;
CREATE TEMPORARY TABLE ids_to_delete ( id BIGINT PRIMARY KEY );

DROP TEMPORARY TABLE IF EXISTS distinct_groups;
CREATE TEMPORARY TABLE distinct_groups (
    seq              BIGINT AUTO_INCREMENT PRIMARY KEY,
    audience_def_id  BIGINT,
    segment_def_id   BIGINT,
    KEY (audience_def_id, segment_def_id)
);

INSERT INTO distinct_groups (audience_def_id, segment_def_id)
SELECT audience_def_id, segment_def_id
  FROM (
        SELECT DISTINCT audience_def_id, segment_def_id
          FROM segment_stats_def
       ) g
 WHERE (@cur_aud IS NULL)
    OR (g.audience_def_id,  g.segment_def_id) >
       (@cur_aud,            @cur_seg)
 ORDER BY g.audience_def_id, g.segment_def_id
 LIMIT @MAX_GROUPS_PER_RUN;

SELECT 'PRE-CHECK: groups queued for THIS run' AS status,
       COUNT(*) AS group_count FROM distinct_groups;

-- ---------------------------------------------------------------------
-- 4. PROCEDURE
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS RetentionBatchDelete;

DELIMITER $$
CREATE PROCEDURE RetentionBatchDelete(
    IN records_to_keep  INT,
    IN batch_limit      INT,
    IN sleep_seconds    DECIMAL(5,2)
)
BEGIN
    DECLARE v_audience        BIGINT;
    DECLARE v_segment         BIGINT;
    DECLARE v_done            INT DEFAULT 0;
    DECLARE v_group_total_ids INT DEFAULT 0;
    DECLARE v_total_deleted   BIGINT DEFAULT 0;
    DECLARE v_batch_count     INT DEFAULT 0;
    DECLARE v_groups_processed INT DEFAULT 0;

    DECLARE group_cursor CURSOR FOR
        SELECT audience_def_id, segment_def_id
          FROM distinct_groups
         ORDER BY seq;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS batch_queue;
    CREATE TEMPORARY TABLE batch_queue ( id BIGINT PRIMARY KEY );

    OPEN group_cursor;

    group_loop: LOOP
        FETCH group_cursor INTO v_audience, v_segment;
        IF v_done = 1 THEN LEAVE group_loop; END IF;

        TRUNCATE TABLE ids_to_delete;

        INSERT INTO ids_to_delete (id)
        SELECT id
          FROM segment_stats_def
         WHERE audience_def_id = v_audience
           AND segment_def_id  = v_segment
         ORDER BY execution_id DESC
         LIMIT 18446744073709551615 OFFSET records_to_keep;

        SELECT COUNT(*) INTO v_group_total_ids FROM ids_to_delete;

        IF v_group_total_ids > 0 THEN
            batch_loop: LOOP
                TRUNCATE TABLE batch_queue;

                INSERT INTO batch_queue (id)
                SELECT id FROM ids_to_delete LIMIT batch_limit;

                SELECT COUNT(*) INTO v_batch_count FROM batch_queue;
                IF v_batch_count = 0 THEN LEAVE batch_loop; END IF;

                START TRANSACTION;
                    DELETE s1 FROM segment_stats_def s1
                      JOIN batch_queue b ON s1.id = b.id;
                    DELETE d  FROM ids_to_delete d
                      JOIN batch_queue b ON d.id = b.id;
                COMMIT;

                SET v_total_deleted = v_total_deleted + v_batch_count;
                DO SLEEP(sleep_seconds);
            END LOOP batch_loop;
        END IF;

        SET v_groups_processed = v_groups_processed + 1;

        -- Advance persistent checkpoint after EACH group → kill-safe.
        UPDATE segment_stats_def_retention_cursor
           SET last_audience_id  = v_audience,
               last_segment_id   = v_segment,
               groups_done_total  = groups_done_total  + 1,
               rows_deleted_total = rows_deleted_total + v_group_total_ids
         WHERE id = 1;

        IF v_groups_processed MOD 100 = 0 THEN
            SELECT CONCAT('Progress: ', v_groups_processed,
                          ' groups this run, ',
                          v_total_deleted, ' rows deleted this run') AS status;
        END IF;
    END LOOP group_loop;

    CLOSE group_cursor;

    SELECT CONCAT('RUN COMPLETE. Groups this run: ', v_groups_processed,
                  ', Rows deleted this run: ', v_total_deleted) AS status;

    DROP TEMPORARY TABLE IF EXISTS batch_queue;
END$$
DELIMITER ;

-- ---------------------------------------------------------------------
-- 5. EXECUTE
-- ---------------------------------------------------------------------
CALL RetentionBatchDelete(@RECORDS_TO_KEEP, @BATCH_SIZE, @SLEEP_BETWEEN_BATCHES);

-- ---------------------------------------------------------------------
-- 6. VERIFICATION
-- ---------------------------------------------------------------------
SELECT 'CHECKPOINT AFTER RUN' AS status, last_audience_id, last_segment_id,
       groups_done_total, rows_deleted_total, updated_at
  FROM segment_stats_def_retention_cursor WHERE id = 1;

SELECT 'REMAINING groups still over threshold (sample)' AS status,
       audience_def_id, segment_def_id, cnt
  FROM (
        SELECT audience_def_id, segment_def_id, COUNT(*) AS cnt
          FROM segment_stats_def
         GROUP BY audience_def_id, segment_def_id
        HAVING cnt > @RECORDS_TO_KEEP
         LIMIT 10
       ) AS check_groups;

-- ---------------------------------------------------------------------
-- 7. CLEANUP
-- ---------------------------------------------------------------------
DROP TEMPORARY TABLE IF EXISTS ids_to_delete;
DROP TEMPORARY TABLE IF EXISTS distinct_groups;
DROP PROCEDURE IF EXISTS RetentionBatchDelete;
SET SQL_SAFE_UPDATES = 1;

-- When groups_done_total has covered all groups and verification returns 0 rows:
--   DROP TABLE segment_stats_def_retention_cursor; 