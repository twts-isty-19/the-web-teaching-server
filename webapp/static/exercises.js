
let main_node = document.querySelector("#exercises-app");
let chapter_id = main_node.dataset.chapterId;
let DB = DOM_Builder;

async function get_answers() {
    let response = await fetch("/exercises/" + chapter_id, {
        headers: {"Content-Type": "application/json"}
    });

    return await response.json();
}

function view_answers(answers) {
    main_node.innerHTML = '';
    if(answers.current_question >= answers.questions.length) {
        main_node.appendChild(
            DB.div({}, [
                 'You have answered all the questions',
                 DB.button(
                    {onclick: function(){ restart(answers);}},
                    ["Start over!"]
                )
            ])
        );
        return;
    }

    let question = answers.questions[answers.current_question]
    main_node.appendChild(
        DB.div({}, [
            DB.h2({}, [answers.chapter_name]),
            "Question " + (answers.current_question + 1) + "/" + answers.questions.length,
            DB.rawInDiv({}, question.title),
            DB.form({onsubmit: function(){ validate_answer(answers);}}, [
                DB.input({
                    type: "text",
                    value: question.answer === null ? "" : question.answer,
                    placeholder: "Enter your answer here!",
                    id: "answer-input"
                }, []),
                DB.input({
                    type: "submit",
                    value: "Validate and next question!"
                }, [])
            ])
        ])
    );
}

function validate_answer(answers) {
    let answer = document.querySelector("#answer-input").value;
    let question = answers.questions[answers.current_question];
    question.answer = answer;
    fetch("/exercises/" + chapter_id, {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(answers)
    })
    answers.current_question += 1;
    view_answers(answers);
}

function restart(answers) {
    answers.current_question = 0;
    view_answers(answers);
}



async function run() {
    let answers = await get_answers();
    view_answers(answers);
}

run();