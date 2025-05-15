from marshmallow import Schema, fields, validate


class MessageListSchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    pageSize = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    sort = fields.Str(load_default="desc", validate=validate.OneOf(["asc", "desc"]))


class MessageSchema(Schema):
    id = fields.Int(required=True)
    received_at = fields.DateTime()
    sender = fields.Str()
    subject = fields.Str()
    body = fields.Str()  # sanitized content
