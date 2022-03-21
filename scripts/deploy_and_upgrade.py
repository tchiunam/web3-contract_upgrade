from brownie import (Box, BoxV2, Contract, ProxyAdmin,
                     TransparentUpgradeableProxy, network)

from scripts.utility.helper import encode_function_data, get_account, upgrade


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})

    proxy_admin = ProxyAdmin.deploy({"from": account})
    initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, box_encoded_initializer_function, {"from": account})
    print(f"Deployed proxy to {proxy}")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    box_v2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(
        account=account, proxy=proxy, new_implementation_address=box_v2.address, proxy_admin_contract=proxy_admin)
    upgrade_transaction.wait(1)
    print("Upgraded proxy")

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
