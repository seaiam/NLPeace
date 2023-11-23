// Get the modal
var modal = document.getElementById("myModal");
var btn = document.getElementById("editBtn");
var span = document.getElementsByClassName("close")[0];

const handleOnPhotoClick = () => {
    const upload = document.getElementById("id_image");
    upload.click();
}

const handleOnDeletePhotoClick = () => {
    const upload = document.getElementById("id_image");
    const div = document.getElementById("preview_image");
    const image = div.getElementsByTagName('IMG')[0];
    upload.value = null;
    div.style.display = "none"; 
    image.src = "#";
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
    const upload = document.getElementById("id_image");
    const div = document.getElementById("preview_image");
    if (upload && div) {
        const image = div.getElementsByTagName("IMG")[0]
        upload.addEventListener('change', e => {
            const reader = new FileReader()
            if (e.target.files && e.target.files[0]) {
                reader.onload = () => {
                    image.src = reader.result;
                };
                reader.readAsDataURL(e.target.files[0]);
                div.style.display = "block";
            }
        });
    }
});



// When the user clicks on the button, open the modal
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user closes the modal
span.onclick = function() {
    modal.style.display = "none";
}

// Closing model when the user clicks outside of the modal
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Saving the bio when the save button is clicked.
var saveBtn = document.getElementById("saveBtn");
var bioInput = document.getElementById("bioInput");
saveBtn.onclick = function() {
    console.log("Bio saved:", bioInput.value);
    modal.style.display = "none";
}

//Comment
$(document).ready(() => {
    const upload = document.getElementById("id_image");
    const div = document.getElementById("preview_image");
    if (upload && div) {
        const image = div.getElementsByTagName("IMG")[0]
        upload.addEventListener('change', e => {
            const reader = new FileReader()
            if (e.target.files && e.target.files[0]) {
                reader.onload = () => {
                    image.src = reader.result;
                };
                reader.readAsDataURL(e.target.files[0]);
                div.style.display = "block";
            }
        });
    }
});
