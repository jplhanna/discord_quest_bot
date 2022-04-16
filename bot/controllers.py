from discord.ext.commands import Context


def check_and_register_user(ctx: Context) -> str:
    if ctx.author.id:  # TODO check if this id already exists in the db
        return "You have already registered"
    # TODO Insert new user into db
    return "You have been registered, prepare for adventure!"
