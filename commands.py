from discord.ext import commands
from currency_api import get_currency_conversion, get_amount_conversion, get_historical_data, get_currencies
from datetime import date, timedelta

def setup_commands(bot):
    @bot.command()
    async def help(ctx):
        commands_list = "\n".join(bot_commands)

        await ctx.send(f"Available commands:\n```{commands_list}```")


    @bot.command()
    async def rate(ctx, *args):
        if not args:
            await ctx.send("Please provide the base currency\n (e.g., !rate USD)")
            return

        base_currency = args[0].upper()
        target_currency = args[1].upper()
        rate = get_currency_conversion(base_currency, target_currency)
        await ctx.send(f'{base_currency.upper()} To {target_currency.upper()} is {rate}')


    @bot.command()
    async def convert(ctx, *args):
        if not args:
            await ctx.send("Please use the following format to convert currencies:\n"
                           "`!convert [amount] [from_currency] [to_currency]`\n"
                           "For example: `!convert 10000 USD JPY`")
            return

        amount = args[0]
        base_currency = args[1].upper()
        target_currency = args[2].upper()
        result = get_amount_conversion(amount, base_currency, target_currency)
        await ctx.send(f'{amount} {base_currency} = {result} {target_currency}')


    @bot.command()
    async def currencies(ctx):
        major_currencies = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY"]

        currency_list = "\n".join(major_currencies)
        get_currencies('fiat')

        await ctx.send(f"Major currencies: \n{currency_list}")

    @bot.command()
    async def history(ctx, base_currency, target_currency, time_span):
        print("....Enter the function...")
        if time_span not in ["1d", "1w", "1y", "5y", "10y"]:
            await ctx.send("Invalid time span. Please use 1d, 1w, 1y, 5y or 10y")

        end_date = date.today()
        if time_span == "1d":
            print("...1d...")
            start_date = end_date - timedelta(days=1)
            print('start date for 1d', start_date)
        elif time_span == "1w":
            print("...1w...")
            start_date = end_date - timedelta(weeks=1)
            print('start date for 1w', start_date)
        elif time_span == "6m":
            start_date = end_date - timedelta(weeks=26)
            print('start date for 6m', start_date)
        elif time_span == "1y":
            print("...1y...")
            start_date = end_date - timedelta(days=365)
        elif time_span == "5y":
            print("...5y...")
            start_date = end_date - timedelta(days=5 * 365)
        elif time_span == "10y":
            print("...10y...")
            start_date = end_date - timedelta(days=10 * 365)

        historical_data = get_historical_data(base_currency, target_currency, start_date)
        print("...historical data... creating...", historical_data)
        if not historical_data:
            await ctx.send("Failed to fetch historical data")
            return

        current_currency_rate =  get_currency_conversion(base_currency, target_currency)

        percentage_change = ((current_currency_rate - historical_data ) / historical_data) * 100
        await ctx.send(f"The exchange rate for {base_currency}/{target_currency} changed by {percentage_change:.2f}% over the past {time_span}.")


