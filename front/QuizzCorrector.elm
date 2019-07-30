module QuizzCorrector exposing (Model, Question)

import Browser
import Browser.Dom
import Browser.Events
import Dict exposing (Dict)
import Element exposing (..)
import Element.Background as Background
import Element.Border as Border
import Element.Font as Font
import Element.Input as Input
import Element.Region as Region
import Html exposing (Html)
import Html.Attributes as Attributes
import Html.Parser
import Html.Parser.Util exposing (toVirtualDom)
import Http
import Json.Decode as Decode exposing (Decoder, Value)
import Json.Encode as Encode
import List.Extra as List


type alias Model =
    { quizzName : String
    , questions : List Question
    , selection : Selection
    }


type Selection
    = FirstNotMarked
    | Manual SelectionStep


type SelectionStep
    = Init
    | StepAnswer Int String


type alias Question =
    { title : String
    , answers : List Answer
    , gradesByAnswer : Dict String Int
    , coefficient : Float
    }


type alias Answer =
    { answer : String
    , students : List String
    }


type alias SelectedAnswer =
    { answer : Answer
    , question : Question
    , questionNumber : Int
    }


questionDecoder : Decoder Question
questionDecoder =
    Decode.map4 Question
        (Decode.field "title" Decode.string)
        (Decode.field "answers" (Decode.list answerDecoder))
        (Decode.field "gradesByAnswer" (Decode.dict Decode.int))
        (Decode.field "coefficient" Decode.float)


getSelectedAnswer : Model -> Maybe SelectedAnswer
getSelectedAnswer model =
    case model.selection of
        FirstNotMarked ->
            List.indexedMap Tuple.pair model.questions
                |> List.filterMap
                    (\( i, question ) ->
                        getUngradedAnswer question
                            |> Maybe.map
                                (\answer ->
                                    { answer = answer
                                    , question = question
                                    , questionNumber = i
                                    }
                                )
                    )
                |> List.head

        Manual Init ->
            model.questions
                |> List.head
                |> Maybe.andThen
                    (\question ->
                        List.head question.answers
                            |> Maybe.map
                                (\answer ->
                                    { answer = answer
                                    , question = question
                                    , questionNumber = 0
                                    }
                                )
                    )

        Manual (StepAnswer questionNumber answerStr) ->
            model.questions
                |> List.getAt questionNumber
                |> Maybe.andThen
                    (\question ->
                        List.filter (.answer >> (==) answerStr) question.answers
                            |> List.head
                            |> Maybe.map
                                (\answer ->
                                    { answer = answer
                                    , question = question
                                    , questionNumber = questionNumber
                                    }
                                )
                    )


selectedAnswerToValue : Int -> SelectedAnswer -> Value
selectedAnswerToValue mark selectedAnswer =
    Encode.object
        [ ( "questionNumber", Encode.int selectedAnswer.questionNumber )
        , ( "answer", Encode.string selectedAnswer.answer.answer )
        , ( "mark", Encode.int mark )
        ]


getUngradedAnswer : Question -> Maybe Answer
getUngradedAnswer question =
    question.answers
        |> List.filter (\answer -> Dict.get answer.answer question.gradesByAnswer == Nothing)
        |> List.head


answerDecoder : Decoder Answer
answerDecoder =
    Decode.map2 Answer
        (Decode.field "answer" Decode.string)
        (Decode.field "students" (Decode.list Decode.string))


type Msg
    = Mark Int SelectedAnswer
    | GotQuestions (Result Http.Error (List Question))
    | SelectQuestion Int
    | SelectQuestionAnswer Int String
    | SelectAutomatic
    | SelectManual


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Mark mark selectedAnswer ->
            ( model
            , Http.post
                { url = "mark-answer/"
                , body =
                    Http.jsonBody <|
                        selectedAnswerToValue mark selectedAnswer
                , expect = Http.expectJson GotQuestions (Decode.list questionDecoder)
                }
            )

        GotQuestions (Ok questions) ->
            ( { model | questions = questions }, Cmd.none )

        GotQuestions (Err e) ->
            let
                _ =
                    Debug.log "Http error:" e
            in
            ( model, Cmd.none )

        SelectAutomatic ->
            ( { model | selection = FirstNotMarked }, Cmd.none )

        SelectQuestion questionNumber ->
            ( { model
                | selection =
                    model.questions
                        |> List.getAt questionNumber
                        |> Maybe.andThen (.answers >> List.head)
                        |> Maybe.map (.answer >> StepAnswer questionNumber >> Manual)
                        |> Maybe.withDefault FirstNotMarked
              }
            , Cmd.none
            )

        SelectQuestionAnswer questionNumber answer ->
            ( { model | selection = Manual <| StepAnswer questionNumber answer }
            , Cmd.none
            )

        SelectManual ->
            ( { model | selection = Manual Init }, Cmd.none )


view : Model -> Html Msg
view model =
    Element.layout [ width fill ] <|
        column
            [ width fill, padding 10 ]
            [ el [ Region.heading 2, Font.heavy ] (text model.quizzName)
            , row
                [ width fill
                , spacing 5
                ]
                [ el [ width (px 400), alignTop ] (viewSelectionPanel model)
                , case getSelectedAnswer model of
                    Just selectedAnswer ->
                        row
                            [ width fill
                            , Border.widthEach { right = 0, left = 1, top = 0, bottom = 0 }
                            , Border.color (rgb 0.5 0.5 0.5)
                            , padding 5
                            ]
                            [ viewAnswer selectedAnswer
                            , viewStudents selectedAnswer.answer.students
                            ]

                    Nothing ->
                        text "All the answers have been marked!"
                ]
            ]


viewSelectionPanel : Model -> Element Msg
viewSelectionPanel model =
    column
        [ width fill
        , spacing 10
        , padding 5
        ]
        (case model.selection of
            FirstNotMarked ->
                [ text "Mode: automatic"
                , Input.button [ Background.color <| rgb 1 0 0, padding 20 ]
                    { onPress = Just <| SelectManual
                    , label = text "Manual"
                    }
                ]

            Manual step ->
                [ text "Mode: manual"
                , Input.button [ Background.color <| rgb 1 0 0, padding 20 ]
                    { onPress = Just SelectAutomatic
                    , label = text "Automatic"
                    }
                , case step of
                    Init ->
                        row [ width fill, spacing 5 ]
                            [ viewNumberingColumn <| List.length model.questions
                            , viewQuestionList model.questions
                            ]

                    StepAnswer questionNumber answerStr ->
                        column [ spacing 10 ]
                            [ Input.button [ Background.color (rgb 0.8 0.8 0.1), padding 10 ]
                                { label = text "Select question"
                                , onPress = Just SelectManual
                                }
                            , model.questions
                                |> List.getAt questionNumber
                                |> Maybe.map
                                    (\question ->
                                        column [ spacing 10, padding 5 ]
                                            (question.answers
                                                |> List.map
                                                    (\answer ->
                                                        if answer.answer == answerStr then
                                                            el [ Background.color (rgb 0 0.8 0.2) ] (text answerStr)

                                                        else
                                                            Input.button []
                                                                { label = text answer.answer
                                                                , onPress =
                                                                    Just <| SelectQuestionAnswer questionNumber answer.answer
                                                                }
                                                    )
                                            )
                                    )
                                |> Maybe.withDefault (text "Error...")
                            ]
                ]
        )


viewQuestionList : List Question -> Element Msg
viewQuestionList questions =
    questions
        |> List.indexedMap Tuple.pair
        |> List.map
            (\( i, question ) ->
                Input.button []
                    { onPress = Just <| SelectQuestion i
                    , label = text question.title
                    }
            )
        |> column
            [ spacing 10
            , padding 5
            , clip
            , width fill
            ]


viewNumberingColumn : Int -> Element Msg
viewNumberingColumn n =
    List.range 0 (n - 1)
        |> List.map
            (\i ->
                Input.button []
                    { onPress = Just <| SelectQuestion i
                    , label = text <| String.fromInt (i + 1)
                    }
            )
        |> column
            [ spacing 10
            , padding 5
            , Border.widthEach { right = 1, left = 0, top = 0, bottom = 0 }
            , Border.color (rgb 0.5 0.5 0.5)
            , Background.color (rgb 0.8 0.8 0.8)
            ]


viewAnswer : SelectedAnswer -> Element Msg
viewAnswer selectedAnswer =
    column [ width <| fillPortion 5, spacing 20 ]
        [ el [ Region.heading 2, Font.bold ]
            (text <|
                "Question "
                    ++ (String.fromInt <| selectedAnswer.questionNumber + 1)
            )
        , paragraph []
            [ case Html.Parser.run selectedAnswer.question.title of
                Ok htmlQuestion ->
                    html <| Html.div [] (toVirtualDom htmlQuestion)

                Err _ ->
                    text selectedAnswer.question.title
            ]
        , el
            [ Region.heading 2
            , Font.bold
            ]
            (text "Answer")
        , paragraph
            [ htmlAttribute <| Attributes.style "white-space" "pre" ]
            [ html <| Html.text selectedAnswer.answer.answer ]
        , case getMark selectedAnswer of
            Just mark ->
                el [ Font.italic ] (text <| "Mark: " ++ String.fromInt mark)

            Nothing ->
                el [ Font.italic ] (text "No mark yet")
        , el [ Region.heading 2, Font.bold ] (text "Select the mark:")
        , row [ spacing 20 ]
            (generateMarkButtons selectedAnswer)
        ]


getMark : SelectedAnswer -> Maybe Int
getMark selectedAnswer =
    Dict.get selectedAnswer.answer.answer selectedAnswer.question.gradesByAnswer


viewStudents : List String -> Element Msg
viewStudents students =
    column [ width <| fillPortion 1 ]
        [ el [ Region.heading 2, Font.bold ] <|
            text <|
                String.fromInt (List.length students)
                    ++ " students:"
        , column [] (List.map text students)
        ]


generateMarkButtons : SelectedAnswer -> List (Element Msg)
generateMarkButtons selectedAnswer =
    List.range 0 4
        |> List.map
            (\i ->
                Input.button
                    [ padding 20
                    , Background.color (rgb 1 0 0)
                    ]
                    { onPress = Just (Mark i selectedAnswer)
                    , label = text <| String.fromInt i
                    }
            )


stringToMark : String -> Maybe Int
stringToMark s =
    case s of
        "0" ->
            Just 0

        "1" ->
            Just 1

        "2" ->
            Just 2

        "3" ->
            Just 3

        "4" ->
            Just 4

        _ ->
            Nothing


decodeMark : SelectedAnswer -> Decoder Msg
decodeMark selectedAnswer =
    Decode.field "key" Decode.string
        |> Decode.andThen
            (\key ->
                case stringToMark key of
                    Just mark ->
                        Decode.succeed <| Mark mark selectedAnswer

                    Nothing ->
                        Decode.fail <| "wrong key for marking: " ++ key
            )


subscriptions : Model -> Sub Msg
subscriptions model =
    case getSelectedAnswer model of
        Just selectedAnswer ->
            Browser.Events.onKeyPress <| decodeMark selectedAnswer

        Nothing ->
            Sub.none


init : { quizzName : String } -> ( Model, Cmd Msg )
init flags =
    ( { questions = [], quizzName = flags.quizzName, selection = FirstNotMarked }
    , Http.get
        { url = "questions/"
        , expect = Http.expectJson GotQuestions (Decode.list questionDecoder)
        }
    )


main =
    Browser.element
        { view = view
        , update = update
        , subscriptions = subscriptions
        , init = init
        }
