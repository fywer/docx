angular.module("DocumentoService", []).
factory ("mostrarModal", function () 
{
    var interfaz =
    {
        main : function (mensaje)
            {
                this.mensaje = mensaje
            },
            setup : function ()
            {
                return { 
                    buttons:[{text: "cool!", key:27/*Esc*/}],
                    focus: { element:0 }
                };
            },
            prepare : function() {
                this.setContent(this.message);
            }
        }
        return interfaz;
    })
    .controller ("Documentos", function ($scope, $http, $window, $document, $compile) 
    {
        $scope.documentos = []
        $scope.$watch('documentos', function(newVal, oldVal) 
        {
            if (newVal !== oldVal) 
            {
                // $scope.$apply(function() 
                // {
                //     var template =  `<div class="list-group" ng-repeat="documentos in documentos" >
                //     <a class="list-group-item list-group-item-action" ng-init="id=documento.nombre"  aria-current="true" ng-click='mostrarDialogo(id)'>
                //         <div class="d-flex w-100 justify-content-between">
                //             <h6 ng-bind="documento.fechaEmision"> {{ documento.RFCReceptor }}</h6>
                //         </div>
                //         <div>
                //             <strong>RFCReceptor:</strong>
                //         </div>
                //         <small>{{ documento.rfcReceptor }}</small>
                //     </a>   
                // </div>`;
                //     // Compilar el HTML con la directiva ng-repeat
                //     var compiledHTML = $compile(template)($scope);
                //     // Adjuntar el HTML compilado al DOM
                //     angular.element(document.getElementById('form_displayfiles"')).append(compiledHTML);
                // });
                
            }
        }, true);
        angular.element($window).on('load', function () 
        {
            console.log("He cargado :P ")
        });
		$scope.fetchData = (urlapi, request) => 
        {
            return new Promise( (resolve, reject) =>
            {
                fetch(urlapi, request).
                then( response => 
                {
                    if ( response.status >= 200 && response.status <= 299 )
                    {
                        resolve(response.json());
                    }
                    else
                    {
                        reject(response.json());
                    }
                }).
                catch(e =>
                {
                    console.log(e)
                    reject(e.json());
                });
            })
        };
		$scope.setFile = (documento) => 
        {
            const request =
                
                {
                    method : 'POST',
                    body : JSON.stringify({'comprobante':documento}),
                    headers :
                    {
                        'Content-Type' : 'application/json; charset=utf-8'
                    }
                }   
			const uri = '/file';
            $scope.fetchData(`${uri}`, request).
            then( mensaje => 
            {
                $scope.documentos.unshift(mensaje);
                console.log(mensaje)
                alertify.success("Se ha almacenado:: "+mensaje["nombre"])
                document.getElementById("bton_cargarfile").value = '';
                const btonuploadfile = document.querySelector("input[form='form_agregarfile']")
                $scope.descargarXML(mensaje["cfdiXml"], mensaje["nombre"] )
                btonuploadfile.disabled = false;
                btonuploadfile.value = "Upload"
            }).
            catch(e =>
            {
                e.then( err => 
                {
                    btonuploadfile = document.querySelector("input[form='form_agregarfile']");
                    console.warn(err);
                    if (err.codigo == '099')
                    {
                        
                        if(!alertify.alertDelete) 
                        { 
                            //define a new dialog
                            alertify.dialog('alertDelete',function ()
                            {
                                return {
                                    main : function( doc )
                                    {                               
                                        this.doc = doc                            
                                        
                                    },
                                    build : function()
                                    {
                                        // var errorHeader = '<span class="fa fa-info-circle fa-2x" '
                                        // +    'style="vertical-align:middle;color:#e10000;">'
                                        // + '</span> <strong>Información</strong>';
                                        // this.setHeader(errorHeader);
                                    },
                                    hooks:
                                    {
                                        // triggered when the dialog is shown, this is seperate from user defined onshow
                                        onshow: function()
                                        {
                                        }
                                    },
                                    setup : function() 
                                    {
                                        return {
                                            options:{
                                                startMaximized:true,
                                                maximizable: false,
                                                closable:false
                                            },
                                            focus: { element:0 }
                                        };
                                    },
                                    prepare : function () 
                                    {
                                        if (this.doc !== undefined) 
                                        {
                                            var regex = /[0-9a-z]{64}/;
                                            id = this.doc['descripcion'].match(regex)
                                            if ( id !== null )
                                            {
                                                contenido = `
                                                <input id="btnEliminar" hidden ng-click=${$scope.delFile(this.doc)}  type="button" value="Eliminar"/> 
                                                `
                                                this.setContent(contenido);
                                            }
                                        }
                                    },
                                }
                            });
                        }
                        else 
                        {
                            alertify.warning('Por favor, intentalo mas tarde. Código: ' + err.descripcion)
                            btonuploadfile.disabled = false;
                            btonuploadfile.value = "Upload"
                        }
                        alertify.alertDelete(err);
                    }
                })
            });
        };
		$scope.uploadFile = () =>
		{
			btonuploadfile = document.querySelector("input[form='form_agregarfile']");
            btonuploadfile.disabled = true;
            btonuploadfile.value = "Loading...";
            btoncargarfile = document.getElementById("bton_cargarfile");
            files= btoncargarfile.files;
			
			try 
            {
                if (files.length == 0) 
                    throw {"descripcion": "No ha seleccionado un archivo."}
                else
                {
                    console.warn(files[0]);
                    file = files[0]
                    let tipo = file["type"].split('/')[1]
                    let type = 0;
                    switch (tipo)
                    {
                        case 'xml':
                            type = 1;
                            break;
                        default:
                            type = 0;
                    }
                    if (type === 0)
                    {
                        throw {"descripcion": "El fomato no es válido."}
                    }
                    else $scope.saveFile(file);  
                }
            } 
            catch (err)
            {
                console.warn(err);
                alertify.warning('Por favor, intentalo mas tarde. Código: ' + err.descripcion)
                btonuploadfile.disabled = false;
                btonuploadfile.value = "Upload";
                return;
            }
		};	
		$scope.saveFile = (file) => 
		{
            file.arrayBuffer().
            then( buffer => {
                const blob = new Blob([new Uint8Array(buffer)], {type : file["type"]});
                const reader  = new FileReader();
                reader.onload = (event) =>
                {
                    let xml64 = window.btoa(reader.result);
                    let decodeData = window.atob(xml64);
                    let buffer = new ArrayBuffer(xml64.length);
                    let view = new Uint8Array(buffer);
                    for (let i = 0; i < xml64.length; i ++)
                    {
                        view[i] = decodeData.charCodeAt(i);
                    }
                    let file = NaN;
                    file = new Blob([view], {type: 'text/xml'});
                    ruta = URL.createObjectURL(file);
                    console.log(file)
                    let formagregarfile = document.querySelectorAll("#form_agregarfile"); 
                    formagregarfile.forEach( item => 
                    {
                        item.disabled = true 
                    });
                    $scope.setFile(xml64);
                }
                reader.readAsBinaryString(blob);
            });
        };
		$scope.showUpload = function ()
        {   
            const sect_upload = document.getElementById("sect_upload")
            if (!sect_upload.hasAttribute("hidden"))
            {
                sect_upload.setAttribute("hidden", "hidden")
            } 
            else
            {
                sect_upload.removeAttribute("hidden")
            }
        };
        $scope.base64ToBytes = function(base64)
        {
            const binString = atob(base64);
            return Uint8Array.from(binString, (m) => m.codePointAt(0));
        };
        $scope.bytesToBase64 = function (bytes)
        {
            const binString = String.fromCodePoint(...bytes);
            return btoa(binString);
        };
        $scope.actualizarComprobante = (comprobante) =>
        {
            console.log(comprobante)
            alertify.confirm(`${comprobante['nombre']}`, "<h6>¿Deseas Timbrar Comprobante?</h6>", 
            function()
            { 
                const request =
                {
                    method : 'PUT',
                    headers :
                    {
                        'Content-Type' : 'application/json; charset=utf-8',
                    },
                    body : JSON.stringify(comprobante),
                }   
			    const uri = '/file';
                const data = $scope.fetchData(`${uri}`, request);
                data.
                then( response => 
                {
                    var documento = response;
                    let nombre = documento['nombre']
                    console.log("Se ha actualizado el documento " + nombre)
                    alertify.success("El comprobante ha sido actualizado.");
                    alertify.closeAll();
                }).
                catch(err =>
                {
                    err.then( e =>
                    {
                        alertify.warning('Por favor, intentalo mas tarde. Código: ' + e.descripcion)
                        console.warn(e);
                        alertify.closeAll();
                    });
                });
                console.log('Se hizo clic en el botón');
            },
            function()
            { 
                alertify.warning('Se ha cancelado la actualización del comprobante.')
                // alertify.closeAll();
                return
            });
        
        };
        $scope.delFile = function (documento)
        {
            var regex = /[0-9a-z]{64}/;
            id = documento['descripcion'].match(regex)
            alertify.confirm(`${documento['descripcion']}`, "<h6>¿Deseas Eliminar Documento?</h6>", 
            function()
            { 
                const request =
                {
                    method : 'DELETE',
                    headers :
                    {
                        'Content-Type' : 'application/json; charset=utf-8'
                    }
                }   
			    const uri = '/file/';
                const data = $scope.fetchData(`${uri}${id}`, request);
                let btonuploadfile = document.querySelector("input[form='form_agregarfile']");
                data.
                then( response => 
                {
                    var documento = response;
                    let nombre = documento['nombre'];
                    $scope.documentos = $scope.documentos.filter( function(valor) 
                    {
                        return nombre !== valor['nombre'];
                    });
                    console.log("Se ha eliminado el documento " + nombre)
                    alertify.success("El comprobante hasido eliminado intenta de nuevo.");
                    alertify.closeAll();
                    btonuploadfile.disabled = false;
                    document.getElementById("bton_cargarfile").value = '';
                    btonuploadfile.value = "Upload";
                }).
                catch(err =>
                {
                    alertify.warning('Por favor, intentalo mas tarde. Código: ' + err.descripcion)
                    btonuploadfile.disabled = false;
                    btonuploadfile.value = "Upload"
                    console.warn(err);
                    alertify.closeAll();
                });
                console.log('Se hizo clic en el botón');
                    // Aquí puedes agregar cualquier acción que desees que ocurra cuando se haga clic en el botón
            },
            function()
            { 
                let btonuploadfile = document.querySelector("input[form='form_agregarfile']");
                alertify.warning('Se ha cancelado la eliminación del documento.')
                btonuploadfile.disabled = false;
                btonuploadfile.value = "Upload"
                alertify.closeAll();
                return
            });
        };
        $scope.descargarXML = function (xmlcomprobante, nombreArchivo)
        {
            // xmlbin = $scope.base64ToBytes(xmlcomprobante)
            // xmlb64 = $scope.bytesToBase64(xmlbin)
            var archivoBlob = new Blob([decodeURIComponent(escape(atob(xmlcomprobante)))], {type: 'text/xml'});
            var urlArchivoXML = $window.URL.createObjectURL(archivoBlob);
            var enlaceDescarga = document.createElement('a');
            enlaceDescarga.href = urlArchivoXML;
            enlaceDescarga.download = nombreArchivo;
            enlaceDescarga.click();
            $window.URL.revokeObjectURL(urlArchivoXML)
        };
        $scope.mostrarDialogo = function (id) 
        {
            if (id == undefined)
            {
                console.error('El id no ha sido definido.')
            }
            else
            {
                if(!alertify.myAlert) 
                { 
                    //define a new dialog
                    alertify.dialog('myAlert',function ()
                    {
                        return {
                            main : function( doc ) {                               
                                this.doc = doc                            
                            },
                        build:function()
                        {
                            var errorHeader = '<span class="fa fa-info-circle fa-2x" '
                            +    'style="vertical-align:middle;color:#e10000;">'
                            + '</span> <strong>Información</strong>';
                            this.setHeader(errorHeader);
                        },
                        hooks:
                        {
                            // triggered when the dialog is shown, this is seperate from user defined onshow
                            onshow: function(){
                                console.log("No soy una tetera.")
                            }
                        },
                        setup : function()
                        {
                            return {
                                options:{
                                    startMaximized:true,
                                    maximizable: false,
                                    closable:false
                                }, 
                                buttons:[
                                {
                                    invokeOnClose: false,
                                    text: "Salir", 
                                    key:27/*Esc*/
                                
                                }],
                                focus: { element:0 }
                            };
                        },
                        prepare : function () 
                        {
                            console.log(this.doc)
                            if (this.doc !== undefined)
                            {
                                contenido = `
                                    <h6>Hash ID</h6>
                                    <p> ${this.doc['nombre']} </p> 
                                    <h6>ID Tipo</h6>
                                    <p> ${this.doc['idTipoDocumento']} </p> 
                                    <h6><small>Cadena Original:</small></h6>
                                    <textarea rows='8' readonly> ${this.doc['cadenaOriginal']} </textarea> 
                                    <h6><small><b>   Emisión:</b> ${this.doc['fechaEmision']}</small></h6>
                                    <h6><small><b>Timbrado:</b> ${this.doc['timbreFiscal']} </small></h6>
                                    <a> <input type="button" hidden ng-click='${$scope.actualizarComprobante(this.doc)}'/></a>
                                `
                                this.setContent(contenido);
                            }
                        },
                        
                    }});
                }
                const request =
                {
                    method : 'GET',
                    headers :
                    {
                        'Content-Type' : 'application/json; charset=utf-8'
                    }
                }
                const uri = '/file/';
                const data = $scope.fetchData(`${uri}${id}`, request);
                data.
                then( response => 
                {
                    var documento = response;
                    alertify.myAlert(documento);
                }).
                catch(e =>
                {
                    console.error(e);
                    window.alert('Por favor, intentalo mas tarde. Código: ' + e);
                });                   
            }  
        };
        $http.get("/file").then ( 
            function (response) 
            {
                console.log(response);
                if (response.data.length > 0) 
                {
                    $scope.documentos = response.data;
                } 
                else
                {
                    alertify.warning("No se han encontrado documentos.");   
                }            
            },
            function (err)    
            {
                console.warn(err.data);
                alertify.warning('Por favor, intentalo mas tarde. Código: ' + err.data.error)
            }
        )
    }
);