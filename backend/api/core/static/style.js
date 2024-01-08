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
    console.log(id)
    const modal = document.getElementById(id);
    console.log(modal)
    if (modal.style.display === "" || modal.style.display === "none") {
        modal.style.display = "block";
    } else {
        modal.style.display = "none";
    }
}

// Uploading Picture
const showFilePicker = (id, formType, event) => {
    event.preventDefault(); 
    const upload = document.getElementById(id);
    upload.setAttribute('data-form-type', formType);
    upload.click();
}

$(document).ready(() => {
    $('input[type="file"]').on('change', function() {
        const formType = $(this).data('form-type');
        const previewDiv = formType === 'edit' ? $('#edit-preview-image') : $('#create-preview-image'); 
        const image = previewDiv.find('img')[0];

        const reader = new FileReader();
        if (this.files && this.files[0]) {
            reader.onload = (e) => {
                image.src = e.target.result;
            };
            reader.readAsDataURL(this.files[0]);
            previewDiv.show();
        }
    });
});

// Delete uploaded image
const handleDeletePostImage = (formType) => {
    let upload, div;

    if (formType === 'create') {
        upload = document.getElementById("create-upload-image");
        div = document.getElementById("create-preview-image");
    } else if (formType === 'edit') {
        upload = document.getElementById("edit-upload-image");
        div = document.getElementById("edit-preview-image");
    }

    if (upload && div) {
        const image = div.getElementsByTagName('IMG')[0];
        upload.value = null;
        div.style.display = "none"; 
        image.src = "#";
    }
}

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
