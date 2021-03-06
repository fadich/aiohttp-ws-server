import aiohttp
from aiohttp import web


clients = []


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    clients.append(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                for client in clients:
                    await client.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/', websocket_handler)])
    web.run_app(app, host='localhost', port=3000)
