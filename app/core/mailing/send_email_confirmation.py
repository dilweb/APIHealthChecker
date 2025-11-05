from textwrap import dedent

from templates.jinja_templates import templates

from app.core.mailing.send_email import send_email
from app.models import User

async def send_email_confirmation(
        user: User,

):
    recipient = user.email
    subject = "Email confirmed successfully"
    plain_content = dedent(
        f"""\
        Dear {recipient},
        Your email address has been successfully confirmed. 
        """
    )

    template = templates.get_template("email-verify/email-verified.html")
    context = {
        "user": user,
    }
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )