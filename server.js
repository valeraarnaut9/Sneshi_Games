const express = require("express");
const path = require("path");
const { createClient } = require("@supabase/supabase-js");
const { v4: uuidv4 } = require("uuid");
const bcrypt = require("bcrypt");


const app = express();


// ---------- EJS ----------

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));


// ---------- Public ----------

app.use(express.static(path.join(__dirname, "public")));


// ---------- Forms ----------

app.use(express.urlencoded({ extended: true }));
app.use(express.json());


// ---------- Supabase ----------

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);



// ---------- Главная ----------

app.get("/", (req, res) => {

    res.redirect("/signin");

});



// ---------- Sign In ----------

app.get("/signin", (req, res) => {

    res.render("signin");

});



// ---------- Sign Up ----------

app.get("/signup", (req, res) => {

    res.render("signup");

});




// ---------- Регистрация ----------

app.post("/signup", async (req, res) => {


    const {
        username,
        display_name,
        password
    } = req.body;



    if (!username || !display_name || !password) {

        return res.send("Fill all fields");

    }



    // Проверка username

    const { data: existingUser } = await supabase
        .from("users")
        .select("userid")
        .eq("username", username)
        .single();



    if (existingUser) {

        return res.send("Username already exists");

    }




    // Генерация userid

    let userid;


    while (true) {

        const randomID =
            Math.floor(
                10000 + Math.random() * 90000
            );


        const { data } = await supabase
            .from("users")
            .select("userid")
            .eq("userid", randomID)
            .single();



        if (!data) {

            userid = randomID;
            break;

        }

    }




    // Хеш пароля

    const passwordHash =
        await bcrypt.hash(password, 10);





    // Создание пользователя

    const { error } = await supabase
        .from("users")
        .insert({

            userid: userid,

            username: username,

            display_name: display_name,

            bio: "No bio",

            password_hash: passwordHash

        });



    if (error) {

        console.log(error);

        return res.send("Database error");

    }




    // Создание сессии


    const token = uuidv4();


    const expires =
        new Date();


    expires.setDate(
        expires.getDate() + 30
    );




    await supabase
        .from("sessions")
        .insert({

            userid: userid,

            token: token,

            device: "Unknown",

            ip: "Unknown",

            expires_at: expires

        });



    res.redirect(
        "/users/" + userid
    );


});





// ---------- Profile ----------


app.get("/users/:userid", async (req, res) => {


    const userid = req.params.userid;



    const { data, error } = await supabase
        .from("users")
        .select(
            "userid, username, display_name, bio"
        )
        .eq("userid", userid)
        .single();



    if (error || !data) {

        return res.status(404)
            .send("User not found");

    }




    const avatarPath =
    `https://guidsuqitwysbgoevmin.supabase.co/storage/v1/object/public/avatars/users-avatars/avatar_${userid}.webp`;



    const defaultAvatar =
    "https://guidsuqitwysbgoevmin.supabase.co/storage/v1/object/public/avatars/default-avatar/default_avatar.webp";




    res.render("profile", {


        username: data.username,

        display_name: data.display_name,

        bio: data.bio,

        userid: data.userid,

        avatar: avatarPath,

        defaultAvatar: defaultAvatar


    });


});





const PORT =
process.env.PORT || 3000;



app.listen(PORT, () => {

    console.log(
        "Server started:",
        PORT
    );

});
