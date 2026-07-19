const express = require("express");
const path = require("path");
const { createClient } = require("@supabase/supabase-js");

const app = express();


// ---------- EJS ----------

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));


// ---------- Public ----------

app.use(express.static(path.join(__dirname, "public")));


// ---------- Body Parser ----------

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


// ---------- Страница входа ----------

app.get("/signin", (req, res) => {

    res.render("signin");

});


// ---------- Страница регистрации ----------

app.get("/signup", (req, res) => {

    res.render("signup");

});


// ---------- Профиль ----------

app.get("/users/:userid", async (req, res) => {

    const userid = req.params.userid;

    const { data, error } = await supabase
        .from("users")
        .select("userid, username, display_name, bio")
        .eq("userid", userid)
        .single();

    if (error || !data) {

        return res.status(404).send("User not found");

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


// ---------- Запуск ----------

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {

    console.log("Server started:", PORT);

});
