from discord.ext import commands


class OneWord(commands.Converter):
    """discord.py converter which ensures the
    argument does not contain spaces"""
    async def convert(self, ctx, argument):
        if " " in argument:
            raise commands.BadArgument("must be one word")
        return argument
