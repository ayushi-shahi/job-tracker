from marshmallow import Schema, fields, validate


class ApplicationCreateSchema(Schema):
    company = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    role = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    location = fields.Str(load_default=None)
    applied_date = fields.Date(required=True)
    notes = fields.Str(load_default=None)
    source = fields.Str(load_default=None, validate=validate.Length(max=100))


class ApplicationUpdateSchema(Schema):
    company = fields.Str(validate=validate.Length(min=1, max=255))
    role = fields.Str(validate=validate.Length(min=1, max=255))
    location = fields.Str()
    applied_date = fields.Date()
    notes = fields.Str()
    source = fields.Str(validate=validate.Length(max=100))


class StatusTransitionSchema(Schema):
    status = fields.Str(required=True)


class StatusHistorySchema(Schema):
    from_status = fields.Str(attribute="from_status.value", allow_none=True)
    to_status = fields.Str(attribute="to_status.value")
    changed_at = fields.DateTime()


class ApplicationResponseSchema(Schema):
    id = fields.Int()
    company = fields.Str()
    role = fields.Str()
    location = fields.Str()
    status = fields.Str(attribute="status.value")
    applied_date = fields.Date()
    notes = fields.Str()
    source = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    status_history = fields.List(fields.Nested(StatusHistorySchema))