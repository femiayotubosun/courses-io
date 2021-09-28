// $(function() {
// 	'use strict';

	
//   $('.form-control').on('input', function() {
// 	  var $field = $(this).closest('.form-group');
// 	  if (this.value) {
// 	    $field.addClass('field--not-empty');
// 	  } else {
// 	    $field.removeClass('field--not-empty');
// 	  }
// 	});

// });



let context = JSON.parse(document.getElementById('djangoData').textContent);
student = context.student
regular = context.regular
max_units = JSON.parse(context.max_units)
carryovers = context.carryovers
course_form = context.course_form
const app = Vue.createApp({
	el: "#app",
	delimiters: ['[[', ']]'],
	data(){
		return {
			// canRegister: false,
			student, regular, carryovers, max_units, course_form,
			
		}
		
	},
	methods:{
		allowCourse(index){
			reg = this.regular[index]
		
			if( (this.course_form.total_current_units + reg.course.course_units <= this.max_units) && (reg.status == "Unapproved")){
				return true
			}
			else {
				return false
			}
		},
		clearRegCarryover(){
			for (el in this.carryovers){
				if (el.status == 'Unapproved'){
					return this.canRegister = false
				
				}
				else{
					return this.canRegister = true
				}
					
			}
		},
	},
	computed:{
		canRegister(){
			return clearRegCarryover()
		}

	}

})

const mountedApp = app.mount('#app')

mountedApp.clearRegCarryover()