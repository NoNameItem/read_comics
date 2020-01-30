def email_verified_context(_request):
    if _request.user.is_authenticated:
        email = _request.user.emailaddress_set.get(primary=True)
        return {"email_verified": email.verified}
    else:
        return {"email_verified": True}
