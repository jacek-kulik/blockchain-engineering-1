from asyncio import run, create_task, Task
from dataclasses import dataclass
from ipv8.community import Community, CommunitySettings
from ipv8.configuration import ConfigBuilder, WalkerDefinition, Strategy, default_bootstrap_defs
from ipv8.util import run_forever
from ipv8.peer import Peer
from ipv8.peerdiscovery.network import PeerObserver
from ipv8.messaging.payload_dataclass import DataClassPayload
from ipv8.lazy_community import lazy_wrapper
from ipv8_service import IPv8

from client3_miner import *
from typing import List

# Already changed, ours now
COMMUNITY_ID = bytes.fromhex("4c61623247726f75705369676e696e67323032a1")

SERVER_PUBLIC_KEY = bytes.fromhex(
    "4c69624e61434c504b3ae3fc099fb56ca3b5e1de9a1c843387f2acdbb78b1bd4350ffde518068a0d246344b10d0d8c355fd0d76873e7d7f7838f3715e025af08f791324495e083331ce6"
)

PUBLIC_KEY_1 = bytes.fromhex(
    "4c69624e61434c504b3a6ddc887fd7a98d41126d24eb4d3349f27683c555698c94b80b0a11bb43c2f6765645e827f4c331c3eb653f1f52d38683423e6b013c25f3157ed8adbf86aa997a"
)
PUBLIC_KEY_2 = bytes.fromhex(
    "4c69624e61434c504b3aea247287365cefd9dfb2bc0916f6b48cc92fb538ba6de6d4e48bc963e53ec457f55086c09ef0141d8b82305528915235be3166e967dc50e0d6c13d8a91108670"
)
# OLD JACEK PUBLIC KEY
# PUBLIC_KEY_2 = bytes.fromhex(
#     "4c69624e61434c504b3ae9a6f3ee192bcb9833fe647728a19e74d6b7fe2e42efe96f4de40d4922aa7a3dcb7c47a5f1776db9902548aab9fb4ef06dd1dc39b12f99f5e8326334ebe7fcd3"
# )
PUBLIC_KEY_3 = bytes.fromhex(
    "4c69624e61434c504b3a87ca1dee80e128d6ad389fb7b2fd1f99bfa86377fdf3815e97b734d767c48840dc818b5467b27b8fad1e434e07005e05eac40a726334a5b3a83b289a51ca097c"
)

PUBLIC_KEYS = [PUBLIC_KEY_1, PUBLIC_KEY_2, PUBLIC_KEY_3]
GROUP_ID = "a6edc7f90a618bd8"


@dataclass
class SubmitTransactionMessage(DataClassPayload[1]):
    sender_key: bytes
    data: bytes
    timestamp: int
    signature: bytes


@dataclass
class SubmitTransactionResponseMessage(DataClassPayload[2]):
    success: bool
    tx_hash: bytes
    message: str


@dataclass
class GetChainHeight(DataClassPayload[3]):
    request_id: int


@dataclass
class GetHeightResponse(DataClassPayload[4]):
    request_id: int
    height: int
    tip_hash: bytes


@dataclass
class GetBlock(DataClassPayload[5]):
    height: int


@dataclass
class BlockResponse(DataClassPayload[6]):
    height: int
    prev_hash: bytes
    txs_hash: bytes
    timestamp: int
    difficulty: int
    nonce: int
    block_hash: bytes
    tx_hashes: bytes

# Trigger dataclass payload compilation.
_ = SubmitTransactionMessage(bytes(0), bytes(0), 0, bytes(0))
_ = SubmitTransactionResponseMessage(False, bytes(0), "")
_ = GetChainHeight(0)
_ = GetHeightResponse(0, 0, bytes(0))
_ = GetBlock(0)
_ = BlockResponse(0, bytes(0), bytes(0), 0, 0, 0, bytes(0), bytes(0))

class BlockchainEngineeringCommunity(Community, PeerObserver):
    community_id = COMMUNITY_ID

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)

        self.add_message_handler(SubmitTransactionMessage, self.on_submit_transaction)
        self.add_message_handler(GetChainHeight, self.on_get_chain_height)
        self.add_message_handler(GetBlock, self.on_get_block)

        self.server = None
        self.peers = [None] * 3
        self.mempool: List[Transaction] = []
        self.task: None | Task = None
        
        self.chain: list[Block] = [genesis_block]
        

    def started(self) -> None:
        print("Started peer")
        print("I am public key:", self.my_peer.public_key.key_to_bin().hex())

        self.network.add_peer_observer(self)

        # Store myself.
        self.peers[MY_ORDER - 1] = self.my_peer

    def on_peer_added(self, peer: Peer) -> None:
        peer_key = peer.public_key.key_to_bin()
        peer_address = peer.address

        print(f"I found: {peer_key.hex()} at {peer_address}")

        if peer_key == SERVER_PUBLIC_KEY:
            print("Found server!")
            self.server = peer

        elif peer_key == PUBLIC_KEY_1:
            print("Found peer1!")
            self.peers[0] = peer

        elif peer_key == PUBLIC_KEY_2:
            print("Found peer2!")
            self.peers[1] = peer

        elif peer_key == PUBLIC_KEY_3:
            print("Found peer3!")
            self.peers[2] = peer
        
        print(f"Current peers state: {[p.address if p else None for p in self.peers]}")
        print(f"Server: {self.server.address if self.server else None}")

    def on_peer_removed(self, peer: Peer) -> None:
        print(f"Peer removed: {peer.public_key.key_to_bin().hex()}")

    def send_to_others(self, payload: DataClassPayload) -> None:
        for p in self.peers:
            if p is None:
                continue
            if p == self.my_peer:
                continue
            self.ez_send(p, payload)
        
    
    def start_pow_search_task(self)  -> None:
        """
        This function (re)starts a PoW search task
        It is called any time a transaction has been added to the mempool.
        """

        if self.task is not None:
            self.task.cancel()
            self.task = None
        
        self.task = create_task(self.pow_search_task())
    
    async def pow_search_task(self) -> None:
        if len(self.mempool) == 0:
            print("Mempool is empty when starting pow search")
            return
        
        block = 
        

    def on_block_found(self, block: Block) -> None:
        print("Found block function called")
        

    @lazy_wrapper(SubmitTransactionMessage)
    def on_submit_transaction(self, peer: Peer, payload: SubmitTransactionMessage) -> None:
        if peer.public_key.key_to_bin() != SERVER_PUBLIC_KEY:
            return
        # TODO: Implementation of SubmitTransaction

        tx = Transaction(
            peer.public_key.key_to_bin(),
            payload.data,
            payload.timestamp,
            payload.signature
            )
        if not verify_transaction_signature(tx):
            print(f"Signature failed verification: {tx}")
            return

        tx_hash = compute_transaction_hash(tx)
        self.mempool.append(tx)
        

        resposne = SubmitTransactionResponseMessage(True, tx_hash,
                                    "Successfully submitted transaction")
        self.ez_send(peer, resposne)

        self.notify_start_search()
    
    @lazy_wrapper(GetChainHeight)
    def on_get_chain_height(self, peer: Peer, payload: GetChainHeight) -> None:
        if peer.public_key.key_to_bin() != SERVER_PUBLIC_KEY:
            return
        # TODO: Implementation of GetChainHeight
    
    @lazy_wrapper(GetBlock)
    def on_get_block(self, peer: Peer, payload: GetBlock) -> None:
        if peer.public_key.key_to_bin() != SERVER_PUBLIC_KEY:
            return
            
        block = self.chain[payload.height]

        response = BlockResponse(
            block.height,
            block.prev_hash,
            block.txs_hash,
            block.timestamp,
            block.difficulty,
            block.nonce,
            block.block_hash,
            b"".join(block.tx_hashes)
        )

        self.ez_send(peer, response)


async def start_client() -> None:
    builder = ConfigBuilder().clear_keys().clear_overlays()
    builder.add_key("me", "curve25519", "myKeys.pem")

    builder.add_overlay(
        "BlockchainEngineeringCommunity",
        "me",
        [WalkerDefinition(Strategy.RandomWalk, -1, {"timeout": 10.0})],
        default_bootstrap_defs,
        {},
        [("started",)],
    )

    await IPv8(
        builder.finalize(),
        extra_communities={
            "BlockchainEngineeringCommunity": BlockchainEngineeringCommunity
        },
    ).start()

    await run_forever()


run(start_client())