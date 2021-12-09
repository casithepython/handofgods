from discord.ext import commands


class OneWord(commands.Converter):
    """discord.py converter which ensures the
    argument does not contain spaces"""
    async def convert(self, ctx, argument):
        if " " in argument:
            raise commands.BadArgument("must be one word")
        return argument


# @TODO: subclasses?
# currently just putting the error message in the first argument
# and showing it to the user
class DatabaseError(Exception):
    """The database didn't like what you tried to do"""
