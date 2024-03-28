// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.19;

contract Chats {

    struct ChatMessage { // represents messages and their timestamps as one datatype together
        address sender;
        string message;
        uint256 timestamp;
    }

    mapping(uint256 => ChatMessage[]) private messages;
    mapping(uint256 => uint256) private counts;
    uint256 private count;

    function create() public {
        messages[count].push(ChatMessage(msg.sender, "Hello World", block.timestamp));
        counts[count] = 1;
        count = count + 1;
    }

    function put(uint256 id, string calldata message) public {
        messages[id].push(ChatMessage(msg.sender, message, block.timestamp));
        counts[id] = counts[id] + 1;
    }

    function get(uint256 id) public view returns (string[] memory) {
        string[] memory messages1 = new string[](counts[id]);
        ChatMessage[] memory messages2 = messages[id];
        for (uint256 i = 1; i < counts[id]; i++) {
            messages1[i] = (messages2[i].message);
        }
        return messages1;
    }
}
