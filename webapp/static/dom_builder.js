/**
 WARNING: this library is designed for educational purpose, don't use
 in production.

 The idea is to provide a similar API to the Html module of Elm:
 all the view is computed from the data model, withou side effect.
*/

(function(){

let events = new Set([
    'onclick',
    'onblur',
    'onchange',
    'onsubmit',
    'onkeyup',
    'onkeydown'
]);

DOM_Builder = {}

function node(tagName, attrs, children) {
    if(typeof attrs !== 'object' || attrs === null) {
        throw "attrs has to be an object";
    }

    if(!Array.isArray(children)) {
        throw "children has to be an array";
    }

    let elt = document.createElement(tagName);

    for(let key in attrs) {
        if(events.has(key.toLowerCase())) {
            elt.addEventListener(key.substring(2).toLowerCase(), attrs[key], false);
        } else {
            elt.setAttribute(key, attrs[key]);
        }
    }


    for(let child of children) {
        if(typeof child === 'string') {
            // The createTextNode seems to sanitize the strings
            elt.appendChild(document.createTextNode(child));
        } else {
            elt.appendChild(child);
        }
    }

    return elt;
}

DOM_Builder.rawInDiv = function(attrs, html) {
    let div = node("div", attrs, []);
    div.innerHTML = html;
    return div;
}

DOM_Builder.node = node;
DOM_Builder.p = function (attrs, children) {
    return node("p", attrs, children);
}

DOM_Builder.div = function (attrs, children) {
    return node("div", attrs, children);
}

DOM_Builder.a = function (attrs, children) {
    return node("a", attrs, children);
}

DOM_Builder.span = function (attrs, children) {
    return node("span", attrs, children);
}

DOM_Builder.nav = function (attrs, children) {
    return node("nav", attrs, children);
}

DOM_Builder.section = function (attrs, children) {
    return node("section", attrs, children);
}

DOM_Builder.h1 = function (attrs, children) {
    return node("h1", attrs, children);
}

DOM_Builder.h2 = function (attrs, children) {
    return node("h2", attrs, children);
}

DOM_Builder.h3 = function (attrs, children) {
    return node("h3", attrs, children);
}

DOM_Builder.h4 = function (attrs, children) {
    return node("h4", attrs, children);
}

DOM_Builder.h5 = function (attrs, children) {
    return node("h5", attrs, children);
}

DOM_Builder.h6 = function (attrs, children) {
    return node("h6", attrs, children);
}

DOM_Builder.li = function (attrs, children) {
    return node("li", attrs, children);
}

DOM_Builder.ul = function (attrs, children) {
    return node("ul", attrs, children);
}

DOM_Builder.input = function (attrs, children) {
    return node("input", attrs, children);
}

DOM_Builder.textarea = function (attrs, children) {
    return node("textarea", attrs, children);
}

DOM_Builder.form = function (attrs, children) {
    return node("form", attrs, children);
}

DOM_Builder.table = function (attrs, children) {
    return node("table", attrs, children);
}

DOM_Builder.tr = function (attrs, children) {
    return node("tr", attrs, children);
}

DOM_Builder.td = function (attrs, children) {
    return node("td", attrs, children);
}

DOM_Builder.button = function (attrs, children) {
    return node("button", attrs, children);
}

})();