from marshmallow import Schema, fields, validate


class InvitationKeySchema(Schema):
    key = fields.Str(required=True, validate=validate.Length(min=1, max=32))
