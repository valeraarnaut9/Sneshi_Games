const openButton =
document.getElementById("openEditProfile");


const closeButton =
document.getElementById("closeEditProfile");


const overlay =
document.getElementById("profileEditOverlay");



if(openButton){


    openButton.onclick = ()=>{

        overlay.classList.add("show");

    };


}





if(closeButton){


    closeButton.onclick = ()=>{

        overlay.classList.remove("show");

    };


}





if(overlay){


    overlay.onclick = (e)=>{


        if(e.target === overlay){

            overlay.classList.remove("show");

        }


    };


}





const form =
document.getElementById("editProfileForm");



if(form){


form.addEventListener("submit", async(e)=>{


    e.preventDefault();



    const display_name =
    document.getElementById("displayNameInput").value;



    const bio =
    document.getElementById("bioInput").value;





    const response =
    await fetch(
        "/api/profile/edit",
        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:JSON.stringify({

                display_name,

                bio

            })

        }
    );





    const data =
    await response.json();





    if(data.success){


        location.reload();


    }
    else{


        alert(data.message);


    }



});


}
