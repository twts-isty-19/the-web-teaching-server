# Clone into Glitch

1. Create an account on https://glitch.com/ and log you in.
2. [Clone this repo in Glitch by clicking this link!](https://glitch.com/edit/#!/remix/the-web-server-base-to-remix)

It can takes a bit of times, you have to wait until the `Tools` button is quiet to be able to actually run the server. If it doesn't work, please
check that you are logged in.

Two users are automatically created with ids:
* stud@dom.org/12345 (student account),
* teach@dom.org/12345 (teacher account).

# Push your work with Git!

Once you are satisfied by your modifications, use Git in order
to push them to the repository.

1. Open the console: `Tools > Full page console` or `Tools > Logs > Console`.
1. Create a new branch with `git checkout -b NAME/FEATURE`. You have to replace `NAME` by your name and `FEATURE` by a few words of description of your edit (no spaces in it!). E.g., if I had improved the global layout I can do `git checkout -b besnier/global-layout`.
1. Add your name and email with the following commands (replace NAME and
    EMAIL with your name and email of course)

    ```
    git config user.name NAME
    git config user.email EMAIL
    ```
1. Then, add all the files you have edited to the "git index" thanks to
    `git add <file1> <file2>`. E.g., I could enter the command:
    `git add webapp/templates/layout.html webapp/static/style.css`
1. Commit the changes: `git commit`.

   The console should open the
   editor `nano`. You will see the list of all the changes which will be commited or not. Check that list carefully; if it didn't match
   what you want, you can abort the commit by exiting the editor
   (`Ctrl + X`).

   If the list is ok, write a short description of your changes
   in the first line (less than 80 characters), and if needed a
   more complete description of your work after this line. E.g.

   ```
   Improve style for the global layout

   Problem: the global layout was ugly
   Solution: write CSS rules and apply them in the HTML
   ```
   (note the empty line between the first line and the rest of the
   description)
1. Push your new branch on the Github server:
    ```
    git push origin NAME/FEATURE
    ```
    where `NAME/FEATURE` is the name of the branch you have
    created previously.
1. Go to https://github.com/, browse to the repository and make a
    "Pull request" for the branch you have just pushed.









