from discord.ext import commands

class OneWord(commands.Converter):
    async def convert(self, ctx, argument):
        if " " in argument:
            raise commands.BadArgument("must be one word")
        return argument