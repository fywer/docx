'use strict'
const handlerERROR = (e) => {
	console.error(e);
    window.alert(e);
    return new Promise( (resolve, reject) => {
		reject();
	});
}
const responseJSON = (response) => {
	console.warn(response);
	if (response.status == 400) {
		return new Promise( (resolve, reject) => {
			reject("No se ha encontrado el recurso solicitado.");
		}); 
	}
	else if (response.status == 401) {
		return new Promise( (resolve, reject) => {
			reject("El usuario no ha sido autorizado.");
        });
    }
    else if (response.status == 404) {
        return new Promise( (resolve, reject) => {
            reject("El recurso no ha sido encontrado.");
        });
	} else if (response.status == 429) {
		return new Promise( (resolve, reject) => {
			reject("Se han enviado demasiadas peticiones en un tiempo deteminado.");
		});
	} else if (response.status == 500) {
		return new Promise( (resolve, reject) => {
			reject();
		});
	}
	return response.json();
}
const saveFile = (event) => {
    event.preventDefault();
    document.querySelector("[form=form_agregarfile]").disabled = true;
    let btoncargarfile = document.getElementById("bton_cargarfile");
    const files= btoncargarfile.files;
    try {
        if (files.length == 0) {
            window.alert("No ha seleccionado un archivo.");
            throw "No ha seleccionado un archivo.";
        }
    } catch (e) {
        console.warn(e);
        document.querySelector("[form=form_agregarfile]").disabled = false;
        return;
    }
    files[0].arrayBuffer().
    then( buffer => {
        const blob = new Blob([new Uint8Array(buffer)], {type : 'application/pdf'});
        const lector = new FileReader();
        lector.onload = (event) => {
            let pdf64 = window.btoa(lector.result);
            let documento = {
                "nombre" : files[0].name,
                "tipo" : files[0].type,
                "tamanio" : files[0].size,
                "contenido" : pdf64
            } 
            const uri = '/file';
            const request = {
                method : 'POST',
                body : JSON.stringify(documento),
                headers : {
                    'Content-Type' : 'application/json; charset=utf-8'
                }
            }
            fetch(uri, request).
            then(responseJSON).
            then( data => {
                window.alert(data.msg);
                document.querySelector("[form=form_agregarfile]").disabled = false;
                btoncargarfile.value = '';
            }).
            catch(handlerERROR);
        }
        lector.readAsBinaryString(blob);
    }).
    catch(handlerERROR);        
}
const pageviewfile = (file) => {
    const sectviewfile = document.querySelector('#sect_viewfile');
    while (sectviewfile.firstChild){
        sectviewfile.removeChild(sectviewfile.firstChild);
    };
    let btonidfile = document.createElement('input');
    btonidfile.setAttribute('id', 'bton_idfile');
    btonidfile.setAttribute('value', file[0].id);
    btonidfile.setAttribute('type', 'hidden');
    sectviewfile.appendChild(btonidfile);
    let itemFrameFile = document.createElement('iframe');
    itemFrameFile.setAttribute('style', `height: ${window.innerHeight}px; width: 100%;`);
    itemFrameFile.setAttribute('src', file[0].ruta);
    sectviewfile.appendChild(itemFrameFile);
    $.mobile.changePage( "#view_file", {
		role : 'page'
	});
}
const listviewFiles = (files) => {
    const listviewfiles = document.querySelector('#listview_files');
    while (listviewfiles.firstChild){
        listviewfiles.removeChild(listviewfiles.firstChild);
    };
    files.forEach(file => {
        let itemList = document.createElement('li');
        itemList.setAttribute('data-icon', 'info');
        itemList.setAttribute('id', file.id);
        let itemLink = document.createElement('a');
        let itemSubtitleNombre = document.createElement('h2');
        itemSubtitleNombre.appendChild(document.createTextNode(file.nombre));
        itemLink.appendChild(itemSubtitleNombre);
        let itemSubtitleTamanio = document.createElement('h3');
        itemSubtitleTamanio.appendChild(document.createTextNode(file.tamanio + ' bytes'));
        itemLink.appendChild(itemSubtitleTamanio);
        let itemParagraphTipo = document.createElement('p');
        itemParagraphTipo.appendChild(document.createTextNode(file.tipo));
        itemLink.appendChild(itemParagraphTipo);
        itemLink.addEventListener('click', (event) => {
            const uri = '/file?id='.concat(file.id);
            const request = {
                method : 'GET',
                headers : {
                    'Content-Type' : 'application/json; charset=utf-8 '
                }
            }
            fetch(uri, request).
            then(responseJSON).
            then(pageviewfile).
            catch(handlerERROR);
        });
        itemList.appendChild(itemLink);
        listviewfiles.appendChild(itemList);
    });
    $("#listview_files").listview('refresh');
};
const getFiles = () => {
    const uri = '/file';
    const request = {
        method: 'GET',
        headers: {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    fetch(uri, request).
    then(responseJSON).
    then(listviewFiles).
    catch(handlerERROR); 
};
const deleteFile = (event) => {
    event.preventDefault();
    document.querySelector("#bton_eliminarfile").disabled = false;
    const btonidfile = document.getElementById('bton_idfile').value;
    const uri = '/file/'.concat(btonidfile);
    const request = {
        method : 'DELETE',
        headers : {
            'Content-Type' : 'application/json; charset=utf-8',
        }
    }
    fetch(uri, request).
    then(responseJSON).
    then( data => {
        $.mobile.changePage( "#list_files", {
            role : 'page'
        });
        window.alert(data.msg);
        document.querySelector("#bton_eliminarfile").disabled = true;
    }).
    catch(handlerERROR);
};
window.addEventListener('load', (event) => {
    const formagregarfile = document.getElementById("form_agregarfile");
    formagregarfile.addEventListener('submit', saveFile);
});
$(document).on("pageshow", "#view_file", (data) => {
    const btoneliminarfila =  document.getElementById("bton_eliminarfile");
    btoneliminarfila.addEventListener('click', deleteFile);
});
$(document).on("pageshow", "#list_files", (data) => {
    getFiles();
});