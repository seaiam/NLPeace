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

const showFilePicker = (id) => {
    const upload = document.getElementById(id);
    upload.click();
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

const handleDeletePostImage = () => {
    const upload = document.getElementById("id_image");
    const div = document.getElementById("preview_image");
    const image = div.getElementsByTagName('IMG')[0];
    upload.value = null;
    div.style.display = "none"; 
    image.src = "#";
}

// Image upload
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

// Comment
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