const componentCleaner = (component) => {
	while (component.firstChild){
 		component.removeChild(component.firstChild);
	};
}
export default {
	'componentCleaner' : componentCleaner
}