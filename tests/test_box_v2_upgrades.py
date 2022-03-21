import pytest
from brownie import (Box, BoxV2, Contract, ProxyAdmin,
                     TransparentUpgradeableProxy, exceptions)
from scripts.utility.helper import encode_function_data, get_account, upgrade


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account}
    )
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})
    upgrade_transaction = upgrade(
        account=account, proxy=proxy, new_implementation_address=box_v2.address, proxy_admin_contract=proxy_admin)
    upgrade_transaction.wait(1)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
