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
import Http
import Json.Decode as Decode exposing (Decoder, Value)
import Json.Encode as Encode


type alias Model =
    { quizzName : String
    , questions : List Question
    }


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
    , question : String
    , questionNumber : Int
    }


questionDecoder : Decoder Question
questionDecoder =
    Decode.map4 Question
        (Decode.field "title" Decode.string)
        (Decode.field "answers" (Decode.list answerDecoder))
        (Decode.field "gradesByAnswer" (Decode.dict Decode.int))
        (Decode.field "coefficient" Decode.float)


selectAnswer : Model -> Maybe SelectedAnswer
selectAnswer model =
    List.indexedMap Tuple.pair model.questions
        |> List.filterMap
            (\( i, question ) ->
                getUngradedAnswer question
                    |> Maybe.map
                        (\answer ->
                            { answer = answer
                            , question = question.title
                            , questionNumber = i
                            }
                        )
            )
        |> List.head


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


view : Model -> Html Msg
view model =
    Element.layout [ width fill ] <|
        column
            [ width fill, padding 10 ]
            [ el [ Region.heading 2, Font.heavy ] (text model.quizzName)
            , case selectAnswer model of
                Just selectedAnswer ->
                    row [ width fill ]
                        [ viewAnswer selectedAnswer
                        , viewStudents selectedAnswer.answer.students
                        ]

                Nothing ->
                    text "All the answers have been marked!"
            ]


viewAnswer : SelectedAnswer -> Element Msg
viewAnswer selectedAnswer =
    column [ width <| fillPortion 5, spacing 20 ]
        [ el [ Region.heading 2, Font.bold ]
            (text <|
                "Question "
                    ++ (String.fromInt <| selectedAnswer.questionNumber + 1)
            )
        , paragraph [] [ text selectedAnswer.question ]
        , el
            [ Region.heading 2
            , Font.bold
            ]
            (text "Answer")
        , paragraph
            [ htmlAttribute <| Attributes.style "white-space" "pre" ]
            [ html <| Html.text selectedAnswer.answer.answer ]
        , el [ Region.heading 2, Font.bold ] (text "Select the mark:")
        , row [ spacing 20 ]
            (generateMarkButtons selectedAnswer)
        ]


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
                    , Background.color (rgb 255 0 0)
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
    case selectAnswer model of
        Just selectedAnswer ->
            Browser.Events.onKeyPress <| decodeMark selectedAnswer

        Nothing ->
            Sub.none


init : { quizzName : String } -> ( Model, Cmd Msg )
init flags =
    ( { questions = [], quizzName = flags.quizzName }
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
