from textwrap import dedent

from templates.jinja_templates import templates

from app.core.mailing.send_email import send_email
from app.models import User

async def send_verification_email(
        user: User,
        verification_link: str,
        verification_token: str
):
    recipient = user.email
    subject = "Please verify your email address"
    plain_content = dedent(
        f"""\
        Dear {recipient},

        Please verify your email address by clicking on the following link:
        {verification_link}
        
        Use this token to verify your email address: 
        {verification_token}
        """
    )

    template = templates.get_template("email-verify/verification-request.html")
    context = {
        "user": user,
        "verification_link": verification_link,
        "verification_token": verification_token,
    }
    html_content = template.render(context)
    await send_email(
        recipient=recipient,
        subject=subject,
        plain_content=plain_content,
        html_content=html_content,
    )