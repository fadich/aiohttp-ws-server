import aiohttp
from aiohttp import web


clients = {}


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    client_id = request.query.get('id')
    if not client_id:
        await ws.close()

    clients[client_id] = ws

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                for key, client in clients.items():
                    if client_id != key:
                        await client.send_str(msg.data + '/from client #{}'
                                              .format(client_id))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/', websocket_handler)])
    web.run_app(app, host='localhost', port=3000)
