from marshmallow import Schema, fields, validate


class MailboxSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Regexp(r"^[A-Za-z0-9._%+-]{1,20}$"),
    )
