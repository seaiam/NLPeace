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


//

    let walletAddress="";

    async function connectWeb3Wallet() {
        if (typeof window != "undefined" && typeof window.ethereum != "undefined") {
            try {
                if (walletAddress.startsWith("0x")) { // all eth wallets start with 0x   
                    toggleModal('crypto-wallet-modal');
                } else {
                const accounts = await window.ethereum.request({method: "eth_requestAccounts"}); // opens MetaMask prompt to sign in with wallet
                walletAddress = accounts[0];
                console.log(walletAddress); // to show account is connected in console
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

    const web3 = new Web3("https://mainnet.infura.io/v3/9f1531079c90406d8062b2533d036a39") //path for infura to connect to ethereum node
    const projectId = "9f1531079c90406d8062b2533d036a39"  // needed information from infura website to access requests

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

    async function connectionStatus() {   // change text of the button 
        var button = document.getElementById("connection");
        var label = document.getElementById("connection");
        var connection;
        
        if (walletAddress.length > 0){
            const balance = await getBalance();     // need to wait to get balance before continuing
            connection = "Wallet: " + walletAddress.substring(0,6)+"...";
            balanceText.innerText = balance;
        } else {
            connection = "<i class='fas fa-link'></i> Connect wallet";
        }
        button.innerHTML = connection;
        label.innerHTML = connection;
        }
    