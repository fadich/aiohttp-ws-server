import aiohttp
from aiohttp import web


clients = {}


class WebSocketResponse(web.WebSocketResponse):

    def __eq__(self, other):
        """Identify client responses for correctly removing/closing etc."""
        return id(self) == id(other)


async def websocket_handler(request):
    ws = WebSocketResponse()
    await ws.prepare(request)

    client_id = request.query.get('id')
    if not client_id:
        await ws.close()

    if not isinstance(clients.get(client_id), list):
        clients[client_id] = []
    clients[client_id] += [ws]

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                for client in clients[client_id]:
                    if client == ws:
                        await client.close()
            else:
                for key, client_list in clients.items():
                    if client_id != key:
                        for client in client_list:
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
