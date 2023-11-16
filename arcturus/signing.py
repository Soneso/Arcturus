
import quart


async def pay(request: quart.Request) -> quart.Response :
    return await quart.render_template("signing.html", res=request.url)

async def tx(request: quart.Request) -> quart.Response :
    return await quart.render_template("signing.html", res=request.url)