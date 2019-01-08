test:
	py.test

testonly:
	py.test --pdb -k "__only"

define compile_file
@echo Building $(1)
solc --bin -o ./contracts/build/ $(1) --overwrite
solc --bin-runtime -o ./contracts/build/ $(1) --overwrite
solc --opcodes -o ./contracts/build/ $(1) --overwrite
solc --hashes -o ./contracts/build/ $(1) --overwrite
@echo ---------
endef

build_contracts:
	$(call compile_file,./contracts/src/branch_identifier.sol)
	$(call compile_file,./contracts/src/add_get.sol)
	$(call compile_file,./contracts/src/hello_world.sol)
	$(call compile_file,./contracts/src/add.sol)
	$(call compile_file,./contracts/src/bank_cfo_vuln.sol)
	$(call compile_file,./contracts/src/symbolic_return.sol)
	$(call compile_file,./contracts/src/set_add.sol)
	$(call compile_file,./contracts/src/address_return.sol)
	$(call compile_file,./contracts/src/password_withdraw.sol)

lint:
	flake8
