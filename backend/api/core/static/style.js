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
