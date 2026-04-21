"""
Shared CDP domain types.

Pydantic models for common structures used across all CDP API endpoints.
Source: apiSpecification/specs/models.json, parameters.json
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Common pagination parameters used across all CDP list endpoints."""

    offset: int = Field(default=0, description="Pagination offset")
    limit: int = Field(default=40, description="Page size")


class CDPError(BaseModel):
    """Standard CDP error response."""

    errorCode: str
    userMessage: str
    developerMessage: str = ""
    moreInfo: str = ""
    resourceDocumentation: str = ""


class ResourceVersion(BaseModel):
    """Version information for versioned resources."""

    id: int
    version: int
    createdBy: str = ""
    createdDate: str = ""
    lastEditedBy: str = ""
    lastEditedDate: str = ""
    label: str = ""
    description: str = ""
    operation: str = ""


class AuditFields(BaseModel):
    """Common audit fields present on most CDP resources."""

    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None


# ---- Permissions API Types ----
# Source: apiSpecification/specs/permissionsAPI.yaml


class Permission(BaseModel):
    """Permission entry used in roles and user assignments."""

    resource: str = Field(description="Resource type: rest, table, column, report, system")
    identifier: str = Field(description="Entity path with optional wildcards (e.g. 'users/*')")
    actions: list[str] = Field(default_factory=list, description="Allowed actions (e.g. GET, POST)")


class RoleInput(BaseModel):
    """Role creation/update payload."""

    id: Optional[int] = None
    name: str
    whitelist: Optional[list[Permission]] = None
    blacklist: Optional[list[Permission]] = None
    included: Optional[list[RoleInput]] = None


class RoleOutput(BaseModel):
    """Role as returned by the API."""

    roleId: int
    roleName: str
    whitelist: Optional[list[Permission]] = None
    blacklist: Optional[list[Permission]] = None
    included: Optional[list[RoleOutput]] = None


class User(BaseModel):
    """CDP user."""

    userId: Optional[int] = None
    userName: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    password: Optional[str] = Field(default=None, description="Write-only, never returned")
    roles: Optional[list[Permission]] = None


class Client(BaseModel):
    """OAuth client definition."""

    id: Optional[int] = None
    clientId: str
    clientSecret: str
    grants: str
    authorities: Optional[str] = None
    scope: Optional[str] = None
    tokenValidity: int
    roles: Optional[list[RoleInput]] = None


# ---- Data Warehouse API Types ----
# Source: apiSpecification/specs/dwAPI.yaml


class DWFilterQuery(BaseModel):
    """
    DW filter query used by entity list endpoints (passed as `fq` query param).

    Structure: Array of filter maps.
    Within a map, conditions are ANDed. Between maps, conditions are ORed.

    Example: [{"age":["gte","18"],"status":["eq","active"]},{"vip":["eq","true"]}]
    Means: (age >= 18 AND status = active) OR (vip = true)

    Operators: eq, lt, lte, gt, gte
    """

    filters: list[dict[str, list[str]]] = Field(
        default_factory=list,
        description="Array of filter maps. Within a map: AND. Between maps: OR.",
    )


class EntityRecord(BaseModel):
    """Generic entity record — shape depends on the resource type."""

    model_config = {"extra": "allow"}


class A360Profile(BaseModel):
    """A360 Customer 360 profile response."""

    model_config = {"extra": "allow"}


class AudienceCountRequest(BaseModel):
    """Audience count request body."""

    segmentDefinition: Optional[dict] = None

    model_config = {"extra": "allow"}


class AudienceCountResponse(BaseModel):
    """Audience count response."""

    count: Optional[int] = None
    jobId: Optional[str] = None
    status: Optional[str] = None

    model_config = {"extra": "allow"}


class TrackingEvent(BaseModel):
    """Tracking event body."""

    eventType: Optional[str] = None
    identityHash: Optional[str] = None
    properties: Optional[dict] = None

    model_config = {"extra": "allow"}


class DataErasureRequest(BaseModel):
    """Data erasure request body (GDPR/CCPA)."""

    identityHash: Optional[str] = None
    email: Optional[str] = None

    model_config = {"extra": "allow"}


class ResourceDescriptor(BaseModel):
    """Resource descriptor returned by /dw/resources."""

    name: str
    label: Optional[str] = None
    description: Optional[str] = None
    uri: Optional[str] = None

    model_config = {"extra": "allow"}


class EntitySchema(BaseModel):
    """Entity schema description returned by ?action=describe."""

    attributes: Optional[list[dict]] = None

    model_config = {"extra": "allow"}


# ---- Campaign API Types ----
# Source: apiSpecification/specs/campaignAPI.json


class CampaignDef(BaseModel):
    """Campaign definition."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    version: Optional[int] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None
    audienceDefId: Optional[int] = None
    channel: Optional[str] = None
    connectorId: Optional[int] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class DispatchDef(BaseModel):
    """Dispatch definition — controls how/when a campaign is sent."""

    id: Optional[int] = None
    name: str
    campaignDefId: Optional[int] = None
    dispatchType: Optional[str] = None
    schedule: Optional[str] = None
    status: Optional[str] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class AudienceDef(BaseModel):
    """Audience definition — defines the target audience for campaigns."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    version: Optional[int] = None
    definition: Optional[dict] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class CampaignRun(BaseModel):
    """A single execution of a campaign."""

    id: Optional[int] = None
    campaignDefId: Optional[int] = None
    status: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    recordsProcessed: Optional[int] = None

    model_config = {"extra": "allow"}


# ---- Config API Types ----
# Source: apiSpecification/specs/configAPI.yaml


class Tenant(BaseModel):
    """CDP Tenant."""

    tenantId: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    model_config = {"extra": "allow"}


class Workflow(BaseModel):
    """Workflow definition."""

    id: Optional[int] = None
    workflowId: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    version: Optional[int] = None
    workflowData: Optional[str] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class WorkflowStep(BaseModel):
    """A single node in a workflow DAG."""

    stepId: Optional[str] = None
    stepName: Optional[str] = None
    stepType: Optional[str] = None
    params: Optional[list[dict]] = None
    enabled: Optional[bool] = None
    fatal: Optional[bool] = None
    version: Optional[int] = None
    mainScript: Optional[str] = None
    mappingScripts: Optional[list[str]] = None

    model_config = {"extra": "allow"}


class WorkflowEdge(BaseModel):
    """Connection between steps in a workflow DAG."""

    id: Optional[int] = None
    step: Optional[str] = None
    parentStep: Optional[str] = None
    operation: Optional[str] = None

    model_config = {"extra": "allow"}


class Schedule(BaseModel):
    """Schedule definition."""

    id: Optional[int] = None
    tenantId: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    referenceId: Optional[int] = None
    startTime: Optional[str] = None
    period: Optional[str] = None
    frequency: Optional[int] = None
    timeZone: Optional[str] = None
    dayOfWeek: Optional[int] = None
    dayOfMonth: Optional[int] = None
    jobData: Optional[str] = None
    shouldStart: Optional[int] = None
    shouldEnd: Optional[int] = None
    concurrency: Optional[int] = None
    timeout: Optional[int] = None
    active: Optional[bool] = None

    model_config = {"extra": "allow"}


class WorkflowJob(BaseModel):
    """A single execution instance of a workflow."""

    jobId: Optional[int] = None
    workflowId: Optional[str] = None
    status: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None

    model_config = {"extra": "allow"}


class UDMPTable(BaseModel):
    """Unified Data Model Platform table."""

    tableId: Optional[int] = None
    name: Optional[str] = None
    columns: Optional[list[dict]] = None

    model_config = {"extra": "allow"}


class DQERule(BaseModel):
    """Data Quality Engine rule."""

    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    ruleType: Optional[str] = None
    expression: Optional[str] = None

    model_config = {"extra": "allow"}


class Cluster(BaseModel):
    """Compute cluster."""

    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = None

    model_config = {"extra": "allow"}


# ---- Connector API Types ----
# Source: apiSpecification/specs/connectorAPI.json


class Connector(BaseModel):
    """Connector definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    connectorType: Optional[str] = None
    channel: Optional[str] = Field(
        default=None, description="Channel: email, export, sms, ads, facebook, any"
    )
    description: Optional[str] = None
    icon: Optional[str] = None
    palette: Optional[str] = None
    userName: Optional[str] = None
    password: Optional[str] = None
    apiURL: Optional[str] = None
    apiKey: Optional[str] = None
    ftpUserName: Optional[str] = None
    ftpPassword: Optional[str] = None
    ftpURL: Optional[str] = None
    ftpPort: Optional[int] = None
    ftpFolderName: Optional[str] = None
    accountId: Optional[str] = None
    privateKey: Optional[str] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


# ---- Predictions API Types ----
# Source: apiSpecification/specs/predictionsAPI.yml


class PredictionParam(BaseModel):
    """Prediction parameter definition."""

    name: Optional[str] = None
    default: Optional[str] = None
    required: Optional[bool] = None

    model_config = {"extra": "allow"}


class PredictionInput(BaseModel):
    """Prediction input configuration."""

    inputType: Optional[str] = Field(
        default=None,
        description="Input type: datasetDef, datAssDef, predictionDef, prediction, mlDef, operation",
    )
    includeAttributes: Optional[list[str]] = None
    excludeAttributes: Optional[list[str]] = None
    filter: Optional[dict] = None

    model_config = {"extra": "allow"}


class PredictionVariant(BaseModel):
    """Prediction variant definition."""

    variantId: Optional[int] = None
    size: Optional[int] = Field(default=None, description="Percentage of samples for this variant")
    input: Optional[PredictionInput] = None
    resources: Optional[list[dict]] = None

    model_config = {"extra": "allow"}


class PredictionDef(BaseModel):
    """Prediction definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    uri: Optional[str] = None
    version: Optional[str] = None
    tenantId: Optional[int] = None
    tags: Optional[list[str]] = None
    params: Optional[list[PredictionParam]] = None
    variants: Optional[list[PredictionVariant]] = None
    code: Optional[str] = None
    isPublished: Optional[bool] = None
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None
    lastPublishedDate: Optional[str] = None
    lastUnpublishedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class PublishRequest(BaseModel):
    """Publish request for predictions."""

    predictionCode: Optional[str] = None
    note: Optional[str] = None
    clearVariantAssignment: Optional[bool] = Field(default=False)
    clearCache: Optional[bool] = Field(default=True)

    model_config = {"extra": "allow"}


class PredictionRequest(BaseModel):
    """Prediction execution request."""

    tenantId: Optional[int] = None
    identityHash: Optional[str] = None
    variantId: Optional[int] = None
    params: Optional[dict[str, str]] = None

    model_config = {"extra": "allow"}


class PredictionResponse(BaseModel):
    """Prediction execution response."""

    tenantId: Optional[int] = None
    identityHash: Optional[str] = None
    variantId: Optional[int] = None
    variantName: Optional[str] = None
    params: Optional[dict[str, str]] = None
    predictionCode: Optional[str] = None
    predictionDefId: Optional[int] = None
    limit: Optional[int] = None
    publishedDate: Optional[str] = None
    resources: Optional[dict[str, str]] = None
    results: Optional[list[dict[str, str]]] = None
    timestamp: Optional[str] = None
    elapsed: Optional[int] = None

    model_config = {"extra": "allow"}


# ---- Alert API Types ----
# Source: apiSpecification/specs/alertAPI.json


class AlertDef(BaseModel):
    """Alert definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    expression: Optional[str] = Field(default=None, description="Alert trigger expression")
    createdBy: Optional[str] = None
    createdDate: Optional[str] = None
    lastEditedBy: Optional[str] = None
    lastEditedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class Alert(BaseModel):
    """Triggered alert (an instance of an alert that fired)."""

    id: Optional[int] = None
    alertdefid: Optional[int] = Field(default=None, description="Parent alert def ID")
    status: Optional[str] = Field(default=None, description="Status: read, hidden")
    message: Optional[str] = None
    datecreated: Optional[str] = None

    model_config = {"extra": "allow"}


# ---- Report API Types ----
# Source: apiSpecification/specs/reportAPI.yml


class DatasetDefOperand(BaseModel):
    """Operand reference in a dataset operation."""

    id: Optional[int] = None
    type: Optional[str] = None

    model_config = {"extra": "allow"}


class DatasetOperation(BaseModel):
    """Dataset operation for combining data sets in reports."""

    id: Optional[int] = None
    operator: Optional[str] = Field(
        default=None, description="Operator: UNION, INTERSECTION, EXCLUDE"
    )
    arguments: Optional[list[DatasetDefOperand]] = None

    model_config = {"extra": "allow"}


class CubicSetDef(BaseModel):
    """Cubic set definition (Saiku-based OLAP query definition)."""

    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = Field(
        default=None, description="Serialized Saiku JSON defining query, cube, etc."
    )

    model_config = {"extra": "allow"}


class ReportDef(BaseModel):
    """Report definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    reportType: Optional[str] = Field(
        default=None, description="Report type: CUBE or RELATIONAL"
    )
    datasetOperation: Optional[DatasetOperation] = None
    cubicSetDef: Optional[CubicSetDef] = None
    versionNumber: Optional[int] = None
    createdby: Optional[int] = None
    createdDate: Optional[str] = None
    editedBy: Optional[int] = None
    editedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class WidgetDef(BaseModel):
    """Widget definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    reportDef: Optional[list[ReportDef]] = None
    visualizationType: Optional[str] = None
    visualizationProperties: Optional[str] = None
    minHeight: Optional[int] = None
    minWidth: Optional[int] = None
    versionNumber: Optional[int] = None
    createdby: Optional[int] = None
    createdDate: Optional[str] = None
    editedBy: Optional[int] = None
    editedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class DashboardRow(BaseModel):
    """Dashboard row within a column."""

    id: Optional[int] = None
    height: Optional[int] = None
    minHeight: Optional[int] = None
    widgetId: Optional[int] = None
    columns: Optional[list[dict]] = Field(
        default=None, description="Nested columns (recursive structure)"
    )

    model_config = {"extra": "allow"}


class DashboardColumn(BaseModel):
    """Dashboard column within a layout."""

    id: Optional[int] = None
    width: Optional[int] = None
    minWidth: Optional[int] = None
    rows: Optional[list[DashboardRow]] = None

    model_config = {"extra": "allow"}


class DashboardLayout(BaseModel):
    """Dashboard layout container."""

    id: Optional[int] = None
    padding: Optional[int] = None
    fixedRatio: Optional[bool] = None
    columns: Optional[list[DashboardColumn]] = None

    model_config = {"extra": "allow"}


class DashboardDef(BaseModel):
    """Dashboard definition."""

    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    widgets: Optional[list[WidgetDef]] = None
    layout: Optional[DashboardLayout] = None
    versionNumber: Optional[int] = None
    createdby: Optional[int] = None
    createdDate: Optional[str] = None
    editedBy: Optional[int] = None
    editedDate: Optional[str] = None

    model_config = {"extra": "allow"}


class CubeMetadata(BaseModel):
    """OLAP cube metadata."""

    uniqueName: Optional[str] = None
    caption: Optional[str] = None
    dimensions: Optional[str] = Field(
        default=None, description="Serialized dimensions definition"
    )
    measures: Optional[str] = Field(
        default=None, description="Serialized measures definition"
    )

    model_config = {"extra": "allow"}


class DimensionValue(BaseModel):
    """Dimension value within an OLAP cube hierarchy level."""

    uniqueName: Optional[str] = None
    name: Optional[str] = None
    caption: Optional[str] = None

    model_config = {"extra": "allow"}


class ExportRequest(BaseModel):
    """Excel export request parameters."""

    filename: Optional[str] = None
    password: Optional[str] = None

    model_config = {"extra": "allow"}


# ---- Query Language API Types ----
# Source: apiSpecification/specs/qlAPI.json


class QueryColumn(BaseModel):
    """Column metadata in query results."""

    name: Optional[str] = None
    label: Optional[str] = None
    token: Optional[str] = None
    type: Optional[str] = None

    model_config = {"extra": "allow"}


class QueryRow(BaseModel):
    """Row in query results."""

    values: Optional[list[str]] = None

    model_config = {"extra": "allow"}


class QueryResult(BaseModel):
    """SQL query result."""

    query: Optional[str] = None
    columns: Optional[list[QueryColumn]] = None
    numColumns: Optional[int] = None
    rows: Optional[list[QueryRow]] = None

    model_config = {"extra": "allow"}


# ---- Cache API Types ----
# Source: apiSpecification/specs/cacheAPI.yaml


class CacheRequest(BaseModel):
    """Cache entry value request — for PUT operations."""

    value: str = Field(description="The value to store in cache (serialized as string)")
    expiryTime: Optional[int] = Field(
        default=None, description="Optional expiry time in seconds"
    )

    model_config = {"extra": "allow"}


class CacheResult(BaseModel):
    """Cache entry result — returned from GET operations."""

    key: Optional[str] = None
    value: Optional[str] = None
    tenantId: Optional[int] = None

    model_config = {"extra": "allow"}


# ---- Security API Types ----
# Source: apiSpecification/specs/securityAPI.yaml


class OAuthTokenResponse(BaseModel):
    """OAuth token response."""

    access_token: Optional[str] = None
    scope: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None

    model_config = {"extra": "allow"}


class LoginResponse(BaseModel):
    """Login response (same shape as OAuth token)."""

    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None

    model_config = {"extra": "allow"}


# ---- Global Actions Types ----
# Source: apiSpecification/specs/globalActions.json


class ResourceAttribute(BaseModel):
    """Attribute in a resource schema."""

    name: Optional[str] = None
    type: Optional[str] = None
    editable: Optional[bool] = None
    format: Optional[str] = None
    isDefault: Optional[bool] = None

    model_config = {"extra": "allow"}


class ResourceSchemaDescription(BaseModel):
    """Resource describe response (schema info)."""

    schema_: Optional[list[ResourceAttribute]] = Field(
        default=None, alias="schema"
    )

    model_config = {"extra": "allow", "populate_by_name": True}


class CollectionDescription(BaseModel):
    """Collection describe response."""

    numItems: Optional[int] = None
    defaultPageSize: Optional[int] = None
    schema_: Optional[ResourceSchemaDescription] = Field(
        default=None, alias="schema"
    )

    model_config = {"extra": "allow", "populate_by_name": True}
