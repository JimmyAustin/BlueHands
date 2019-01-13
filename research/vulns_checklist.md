https://hackernoon.com/hackpedia-16-solidity-hacks-vulnerabilities-their-fixes-and-real-world-examples-f3210eba5148

## Problems

Solved
- 2. Arithmetic Over/Underflow
    - Underflow is proven to work, but the example doesnt work because of not having token checking working.
- 5. DefaultVisibilities

Not Solved
- 1. Reentrancy
- 3. Unexpected Ether
- 4. DelegateCall
- 7. External Contract Referencing
- 9. Unchecked CALL Return Values
- 11. Denial Of Service
- 14. Unintialised Storage Pointers
- 15. Floating Points and Precision
- 16. Tx.Origin Authentication

Out Of Scope
- 6. Entropy Illusion
- 8. Short Address Parameter Attack
- 10. Race Condition
- 12. Block Timestamp Manipulation

## Notes

- 1. Reentrancy
    - Status: Not Started
    - Needed:
        - Different execution contexts?
- 2. Arithmetic Over/Under Flows
    - Status: Solved
    - Needed:
        - Ensure can find error in underflow contract from timelock.sol
- 3. Unexpected Ether
    - Status: NA
- 4. DelegateCall
    - Status: NA
    - Needed:
        - Different execution contexts
- 5. DefaultVisibilities
    - Status: Solved
- 6. Entropy Illusion
    - Out of scope
- 7. External Contract Referencing
    - Status: NA
- 8. Short Address/Parameter Attack
    - Status: Out of scope.
- 9. Unchecked CALL Return values
    - Status: Not checked
    - Needed:
        - Proper execution contexts
- 10. Race Conditions
    - Status: Outside of scope.
- 11. Denial of Service
    - Status: Checkable?
    - Needed:
        - Mentions a block gas limit. Add check for if its possible to inflate func call over block gas limit? Limit is 8 million. Could be expensive to check for.
- 12. Block Timestamp Manipulation
    - Status: Out of scope?
- 13. Constructors with Care
    - Status: Automatically exploitable!
- 14. Uninitialised Storage Pointers
    - Status: Potentially exploitable
        - Needed investigate. Look at the example contracts.
- 15. Floating Points and Precision
    - 
- 16. Tx.Origin Authentication
    - Status: No
    - Needed:
        - This might be a seperate check?
    - Holy shit this is cooked
