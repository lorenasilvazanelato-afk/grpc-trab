import grpc
from concurrent import futures
import grpc_mine_pb2
import grpc_mine_pb2_grpc
import threading
import random
import hashlib

PORT = 8080

_store_tx = {}
_lock_tx = threading.Lock()
_current_tx = 0
_clients_set = set()
_lock_clients = threading.Lock()
_log_winners = []

def make_challenge():
    val = random.randint(1, 5)
    # Setado dificulade de 1 até 5, acima disso o cliente pode demorar para minerar
    print(f"[DEBUG] Desafio criado: {val}")
    return val

def hash_sha1(val: str) -> str:
    return hashlib.sha1(val.encode()).hexdigest()

def create_tx():
    global _current_tx
    with _lock_tx:
        _store_tx[_current_tx] = {'challenge': make_challenge(), 'solution': None, 'winner': -1}
    print(f"[INFO] Tx criada ID={_current_tx}, desafio={_store_tx[_current_tx]['challenge']}")

def random_client_id():
    while True:
        cid = random.randint(1000, 9999)
        with _lock_clients:
            if cid not in _clients_set:
                _clients_set.add(cid)
                return cid

# ========================
# Servicer com todos os métodos
# ========================
class MineServicer(grpc_mine_pb2_grpc.MineServicer):

    def getTransactionId(self, req, ctx):
        with _lock_tx:
            return grpc_mine_pb2.NumResult(result=_current_tx)

    def getChallenge(self, req, ctx):
        tid = req.transactionId
        with _lock_tx:
            tx = _store_tx.get(tid)
            return grpc_mine_pb2.NumResult(result=tx['challenge'] if tx else -1)

    def getTransactionStatus(self, req, ctx):
        tid = req.transactionId
        with _lock_tx:
            tx = _store_tx.get(tid)
            if not tx:
                return grpc_mine_pb2.NumResult(result=-1)
            return grpc_mine_pb2.NumResult(result=1 if tx['solution'] is None else 0)

    def submitChallenge(self, req, ctx):
        global _current_tx
        tid, cid, sol = req.transactionId, req.clientId, req.solution
        with _lock_tx:
            tx = _store_tx.get(tid)
            if not tx:
                return grpc_mine_pb2.NumResult(result=-1)
            if tx['solution'] is not None:
                return grpc_mine_pb2.NumResult(result=2)
            zeros_count = hash_sha1(sol).count('0')
            if zeros_count >= tx['challenge']:
                tx['solution'] = sol
                tx['winner'] = cid
                _log_winners.append((tid, cid))
                print(f"[INFO] Tx {tid} resolvida por cliente {cid} → sol: {sol}")
                _current_tx += 1
                _store_tx[_current_tx] = {'challenge': make_challenge(), 'solution': None, 'winner': -1}
                print(f"[INFO] Nova Tx criada ID={_current_tx}")
                return grpc_mine_pb2.NumResult(result=1)
            else:
                return grpc_mine_pb2.NumResult(result=0)

    def getWinner(self, req, ctx):
        tid = req.transactionId
        with _lock_tx:
            tx = _store_tx.get(tid)
            if not tx:
                return grpc_mine_pb2.NumResult(result=-1)
            return grpc_mine_pb2.NumResult(result=tx['winner'] if tx['winner'] != -1 else 0)

    def getSolution(self, req, ctx):
        tid = req.transactionId
        with _lock_tx:
            tx = _store_tx.get(tid)
            if not tx:
                return grpc_mine_pb2.TaskResult(status=-1, solution="", challenge=0)
            st = 1 if tx['solution'] is None else 0
            return grpc_mine_pb2.TaskResult(status=st, solution=tx['solution'] or "", challenge=tx['challenge'])

    def registerClient(self, req, ctx):
        cid = random_client_id()
        print(f"Cliente registrado → ID={cid}")
        return grpc_mine_pb2.NumResult(result=cid)

# ========================
# Inicialização do servidor
# ========================
def start_server():
    create_tx()
    svr = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_mine_pb2_grpc.add_MineServicer_to_server(MineServicer(), svr)
    svr.add_insecure_port(f'[::]:{PORT}')
    print(f"[SERVER] Miner rodando na porta {PORT}")
    svr.start()
    svr.wait_for_termination()

if __name__ == "__main__":
    start_server()
