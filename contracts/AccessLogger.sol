// File: contracts/AccessLogger.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AccessLogger {
    event AccessLogged(
        address indexed accessor,
        string userEmail,
        string recordName,
        string action,
        uint256 timestamp
    );

    function logAccess(
        string memory userEmail,
        string memory recordName,
        string memory action
    ) public {
        emit AccessLogged(
            msg.sender,
            userEmail,
            recordName,
            action,
            block.timestamp
        );
    }
}