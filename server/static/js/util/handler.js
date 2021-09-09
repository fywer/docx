const error = (e) => {
	console.error(e);
	window.alert('Por favor, intentalo mas tarde. Código: ' + e);
}
const responseJSON = (response) => {
	console.warn(response);
	if (response.status >= 200 && response.status <= 299) {
        return response.json();
	} if (response.status ) {
		return response.json();
	} else {
        return new Promise( (resolve, reject) => {
			reject(response.status);
		});
    } 
}
export default {
	'error' : error,
    'responseJSON' : responseJSON
}