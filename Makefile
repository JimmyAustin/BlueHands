test:
    py.test - -pdb

testonly:
    py.test - -pdb - k "__only"

define compile_file
solc - -bin - o ./contracts/build / $(1) - -overwrite
solc - -bin-runtime - o ./contracts/build / $(1) - -overwrite
solc - -opcodes - o ./contracts/build / $(1) - -overwrite
solc - -hashes - o ./contracts/build / $(1) - -overwrite
endef

build:
    $(call compile_file, ./contracts/src/branch_identifier.sol)
    $(call compile_file, ./contracts/src/add_get.sol)
    $(call compile_file, ./contracts/src/hello_world.sol)
    $(call compile_file, ./contracts/src/add.sol)
    $(call compile_file, ./contracts/src/symbolic_return.sol)

lint:
    flake8
