import eth_utils
from brownie import accounts, config, network

LOCAL_ENVIRONMENTS = [
    "development",
    "mainnet-fork"
]


def get_account(index: int = None, id: str = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_ENVIRONMENTS:
        return accounts[0]
    elif network.show_active() == "ganache-local":
        return accounts.add(config["wallets"]["local-ui"][0]["private_key"])

    return accounts.add(config["wallets"]["metamask"][0]["private_key"])


def encode_function_data(initializer=None, *args):
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(account, proxy, new_implementation_address, proxy_admin_contract=None, initializer=None, *args):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encoded_function_call,
                {"from": account}
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address,
                new_implementation_address,
                {"from": account}
            )
    elif initializer:
        encoded_function_call = encode_function_data(initializer, *args)
        transaction = proxy.upgradeToAndCall(
            new_implementation_address,
            encoded_function_call,
            {"from": account}
        )
    else:
        transaction = proxy.upgradeTo(
            new_implementation_address, {"from": account})

    return transaction
