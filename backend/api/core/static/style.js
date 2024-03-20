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
        const repostCountSpan = repostButton.nextSibling;
        repostButton.classList.toggle('reposted-button');
        repostCountSpan.textContent = "";
        if (data.reposts_count > 0) {
            repostCountSpan.textContent = data.reposts_count;
        }
    }
})
.catch(error => console.error('Error:', error));
}