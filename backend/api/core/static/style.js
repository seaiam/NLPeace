const addFormSubmitListener = (formid, inputid) => {
    if (inputid) {
        const input = document.getElementById(inputid);
        if (input) {
            input.addEventListener("change", () => {
                const form = document.getElementById(formid);
                form.submit();
            });
        }
    }
}

const toggleModal = (id) => {
    const modal = document.getElementById(id);
    if (modal.style.display === "" || modal.style.display === "none") {
        modal.style.display = "block";
    } else {
        modal.style.display = "none";
    }
}

$(document).ready(() => {

    const startPostUpload = document.getElementById("create-upload-image"); 
    const startPostPreviewDiv = document.getElementById("create-preview-image"); 
    if (startPostUpload && startPostPreviewDiv) {
        const image = startPostPreviewDiv.getElementsByTagName("IMG")[0]
        startPostUpload.addEventListener('change', e => {
            updateImagePreview(e, startPostPreviewDiv);
        });
    }

    $(".edit-post-modal").each(function() {
        const modalId = $(this).attr('id');
        const postId = modalId.split('-').pop();
        const editPostUpload = document.getElementById(`edit-upload-image-${postId}`);
        const editPostPreviewDiv = document.getElementById(`edit-preview-image-${postId}`);
        if (editPostUpload && editPostPreviewDiv) {
            editPostUpload.addEventListener('change', e => {
                updateImagePreview(e, editPostPreviewDiv);
            });
        }
    });
});

function updateImagePreview(event, previewDiv) {
    const reader = new FileReader();
    if (event.target.files && event.target.files[0]) {
        reader.onload = () => {
            const image = previewDiv.getElementsByTagName("IMG")[0];
            image.src = reader.result;
        };
        reader.readAsDataURL(event.target.files[0]);
        previewDiv.style.display = "block";
    }
}

// Delete uploaded image
function handleDeletePostImage(previewDivId, postId) {
    const div = document.getElementById(previewDivId);
    const image = div.getElementsByTagName('IMG')[0];
    div.style.display = "none";
    image.src = "#";

    const removeImageFlag = document.getElementById(`remove-image-flag-${postId}`);
    if (removeImageFlag) {
        removeImageFlag.value = "true";
    }
}

// opening tab 1 by default
$(document).ready(() => {
    const post = document.getElementById("defaultOpenPost");
    if (post) {
        post.click();
    }
})

// Script for opening tabs on Profile page
function openPostTab(event, posttabName) {
    var posttabcontent, profiletabbutton;

    posttabcontent = document.getElementsByClassName("posttabcontent");
    for (i = 0; i < posttabcontent.length; i++) {
        posttabcontent[i].style.display = "none";
    }
    
    profiletabbutton = document.getElementsByClassName("profiletabbutton");
    
    for (i = 0; i < profiletabbutton.length; i++) {
        profiletabbutton[i].className = profiletabbutton[i].className.replace(" active", "");
    }
    document.getElementById(posttabName).style.display = "block";
    event.currentTarget.classList.add("active");
}

// Closing model when the user clicks outside of the modal
window.onclick = function(event) {
    if (event.target.classList.contains("popup")) {
        event.target.style.display = "none";
    }
};


// opening tab 1 by default
document.getElementById("defaultOpenPost").click();

// Connecting web3 MetaMask wallet 

let walletAddress="";

async function connectWeb3Wallet() {
    if (typeof window != "undefined" && typeof window.ethereum != "undefined") {
        try {
            if (walletAddress.startsWith("0x")) { // all eth wallets start with 0x   
                toggleModal('crypto-wallet-modal');
            } else {
            const accounts = await window.ethereum.request({method: "eth_requestAccounts"}); // opens MetaMask prompt to sign in with wallet
            walletAddress = accounts[0];    // sets account to walletAddress
            alert("MetaMask wallet successfully connected");
            }
            connectionStatus()
        } catch (err) {
        console.error(err.message); // for troubleshooting
        }
    } else {
        alert("MetaMask wallet not found");
    }
};

function disconnectWallet(){
    walletAddress="";   // sets address to empty so no wallet is connected
    toggleModal('crypto-wallet-modal'); // closes the modal
    connectionStatus(); // updates the button 
    alert("MetaMask wallet disconnected") 
}

const web3 = new Web3("https://sepolia.infura.io/v3/9f1531079c90406d8062b2533d036a39") //path for infura to connect to ethereum node
const projectId = "9f1531079c90406d8062b2533d036a39"  // needed information from infura website to access requests

// retrieve balance from wallet
async function getBalance() { 
    if (walletAddress && web3){
        try {
            const balance = await web3.eth.getBalance(walletAddress);
            return web3.utils.fromWei(balance, 'ether').substring(0,6) + ' ETH'; // change amount from Wei into ETH
        } catch (err) {
            console.error(err.message);
        }
    }
}

let walletSignature = "";
let message = "Please sign to provide verification for this post."
let msg = web3.utils.utf8ToHex(message)

// ask for signature from MetaMask wallet
async function getSignatureFromWeb3Wallet(id){
    const sigElement = document.getElementById(id)
    
    if (walletAddress!=""){     // check if wallet is connected
        const label = document.getElementById("getSignature");

        if(label.innerHTML === '<i class="fa fa-signature"></i> Sign'){     // only get signature and verify it if there is no current signature
            try {
                const signature = await ethereum.request({method: "personal_sign", params: [msg, walletAddress]});  // gets signature using message and wallet address
                sigElement.value = signature;
                console.log("Signature: ", signature);
                verifySignatureForPost(signature);  // verifies if signature is valid or not
            } catch (err) {
                if (err.code === 4001) {    // if the user rejects the signature request (error code in console is 4001)
                    alert("Signature request rejected");
                } else {
                console.error(err.message); // troubleshooting
                }
            }
        } else {    // if label.innerHTML = "Signed", empty the string and change it back to "Sign" to remove the signature
            const walletSignature = ""; 
            label.innerHTML = '<i class="fa fa-signature"></i> Sign';
            label.style.fontStyle = "normal";
            alert("Signature removed");
        }
    } else {    // if not wallet is connected
        alert("No wallet connected, please sign in with MetaMask");
    }
}
// to verify signature of a post
async function verifySignatureForPost(signature){
    try {
        const signatureAddress = await ethereum.request({method: "personal_ecRecover", params: [msg, signature]});
        if (signatureAddress === walletAddress) {
            const label = document.getElementById("getSignature");
            label.innerHTML = '<i class="fa fa-signature"></i> Signed';
            label.style.fontStyle = "italic";
            alert("Signature verified");
        } else {
            const label = document.getElementById("getSignature");
            label.style.fontStyle = "normal";
            alert("Signature not verified");
        }
    } catch (err){
        console.error(err.message); // troubleshooting
    }
}

// created alerts to show success and failure message
function alert(message){

    const duplicateAlert = document.querySelector(".alert"); //check if an alert already exists

    if (duplicateAlert){
        duplicateAlert.remove(); //remove it if there is one
    }

    const alert = document.createElement("div");
    alert.className = "alert alert-warning alert-dismissible fade show ";
    alert.style.position = "absolute";
    alert.style.zIndex = "10000";
    alert.style.top = "10px"; 
    alert.style.left = "50%"; 
    alert.style.transform = "translate(-50%)";
    alert.style.width ="85%";
    alert.style.maxWidth ="1200px";
    
    const alertDismiss = document.createElement("a");
    alertDismiss.href = "#";
    alertDismiss.className = "close";
    alertDismiss.setAttribute("data-dismiss", "alert");
    alertDismiss.setAttribute("aria-label", "close");
    
    alertDismiss.innerHTML = "&times;";
    alert.appendChild(alertDismiss);

    const alertMessage = document.createTextNode(message);
    alert.appendChild(alertMessage);

    document.body.appendChild(alert);
}

window.onload = connectionStatus;   // happens when window loads to make sure all is up to date
// reloads page to get correct data
async function connectionStatus() {   // change text of the button 
    var label = document.getElementById("connection");
    var connection;
    
    if (walletAddress.length > 0){
        const balance = await getBalance();     // need to wait to get balance before continuing
        connection = "<i class='fas fa-wallet'></i> Wallet: " + walletAddress.substring(0,6)+"...";
        balanceText.innerText = balance;
    } else {
        connection = "<i class='fas fa-link'></i> Connect wallet";
    }
    label.innerHTML = connection;
    }
// Pay to verify post
async function payVerification(id) {
        verifyLabel = document.getElementById("getVerification");
        web3VerifyElement = document.getElementById(id);

        if (walletAddress === "") {
            await connectWeb3Wallet();  // if no wallet currently signed in, calls connectWeb3Wallet() to prompt user to sign in
        }
        const message2 = "Would you like to spend 0.000000001 ETH to verify this post? This transaction cannot be undone";    // sends prompt to metamask wallet to get signature from user to allow exchange
        const msg2 = web3.utils.utf8ToHex(message2);   // change it to hex for metamask to use (needed)
        try {
            const signature = await ethereum.request({method: "personal_sign", params: [msg2, walletAddress]});  // get signature from user
            
            if (signature) {   // verifies if signature is received, if it is, send another prompt for transaction with this info
                const tx ={
                    from: walletAddress,
                    to: "0x0cF3BBcD000a4BF5890ff89f39a80E2A73cdd158",
                    value: web3.utils.toWei("0.000000001", "ether")   // sending 0 ether
                };
                
            await ethereum.request({method: "eth_sendTransaction", params: [tx]}); // uses send_transaction method from web3js with tx object as params
            alert("ETH sent, post is verified");
            web3VerifyElement.value = true;
            verifyLabel.innerHTML = '<i class="fas fa-dollar-sign"></i> Verified';
            verifyLabel.style.fontStyle = "italic";
            }

        } catch (err) {
            if (err.code === 4001) {    // if the user rejects the signature request (error code in console is 4001)
                alert("Request to verify post with ETH rejected");
            } else {
            console.error(err.message);
            }
        }
    }



// Post interactions
function likePost(postId) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'postId': postId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            // Updating like count
            const likeLink = document.querySelector(`.like-link[data-post-id="${postId}"]`);
            const likeCountSpan = likeLink.nextSibling.nextSibling;
            likeLink.classList.toggle('post-liked');
            likeCountSpan.classList.toggle('post-liked');
            likeCountSpan.textContent = "";
            if (data.likes_count > 0) {
                likeCountSpan.textContent = data.likes_count;
            }
            console.log(likeCountSpan)
        }
    })
    .catch(error => console.error('Error:', error));
}

function dislikePost(postId) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
    fetch(`/dislike/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'postId': postId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.disliked) {
            // Updating dislike count
            const dislikeLink = document.querySelector(`.dislike-link[data-post-id="${postId}"]`);
            const dislikeCountSpan = dislikeLink.nextSibling.nextSibling;
            dislikeLink.classList.toggle('post-disliked');
            dislikeCountSpan.classList.toggle('post-disliked');
            dislikeCountSpan.textContent = "";
            if (data.dislikes_count > 0) {
                dislikeCountSpan.textContent = data.dislikes_count;
            }
            console.log(dislikeCountSpan)
        }
    })
    .catch(error => console.error('Error:', error));
}

function savePost(postId) {
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
fetch(`/save_post/${postId}/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({ 'postId': postId })
})
.then(response => response.json())
.then(data => {
    const saveButton = document.querySelector(`.bookmark-button[data-post-id="${postId}"]`);
    const saveCountSpan = saveButton.nextSibling.nextSibling;
    saveButton.classList.toggle('bookmarked-button');
    saveCountSpan.classList.toggle('bookmarked-button');
    saveCountSpan.textContent = (data.saves_count > 0) ? data.saves_count : "";
    if (!data.saved) {
        saveButton.classList.remove('bookmarked-button'); 
    }
})
.catch(error => console.error('Error:', error));
}

function repostPost(postId) {
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
fetch(`/repost/${postId}/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({ 'postId': postId })
})
.then(response => response.json())
.then(data => {
    if (data.reposted) {
        // Updating repost count
        const repostButton = document.querySelector(`.repost-button[data-post-id="${postId}"]`);
        const repostCountSpan = repostButton.nextSibling.nextSibling;
        repostButton.classList.toggle('reposted-button');
        repostCountSpan.classList.toggle('reposted-button');
        repostCountSpan.textContent = "";
        if (data.reposts_count > 0) {
            repostCountSpan.textContent = data.reposts_count;
        }
    }
})
.catch(error => console.error('Error:', error));
}