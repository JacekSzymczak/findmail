from marshmallow import Schema, fields


class MessageSchema(Schema):
    id = fields.Str(required=True)
    imap_id = fields.Str()
    received_at = fields.DateTime()
    sender = fields.Str()
    subject = fields.Str()
    body = fields.Str()  # sanitized content
