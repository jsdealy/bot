#include <dpp/dpp.h>
#include <cstdlib>
#include <fstream>
#include "jtb/jtbstr.h"



	 
int main() {
    dpp::cluster bot(std::getenv("DISCORD_TOKEN"));

    bot.on_log(dpp::utility::cout_logger());

    bot.on_ready([&bot](const dpp::ready_t& event) {
	/* Create a new global command on ready event */
	if (dpp::run_once<struct make_list_slashcommand>()) { 
	    dpp::slashcommand newcommand("list", "manipulate your own personal list of films", bot.me.id);
	    newcommand.add_option(
		dpp::command_option(dpp::co_string, "action", "The list action you want to perform", true).set_auto_complete(true)
	    );
	    /* Register the command */
	    bot.global_command_create(newcommand);
	};
	if (dpp::run_once<struct make_pick_slash_command>()) { 
	    dpp::slashcommand newcommand("pick", "pick a film", bot.me.id);
	    /* Register the command */
	    bot.global_command_create(newcommand);
	};
    });

    /* The interaction create event is fired when someone issues your commands */
    bot.on_slashcommand([&bot](const dpp::slashcommand_t & event) {
	/* Check which command they ran */
	if (event.command.get_command_name() == "pick") {

	}
	if (event.command.get_command_name() == "list") {
	    /* Fetch a parameter value from the command parameters */
	    std::string action = std::get<std::string>(event.get_parameter("action"));
	    /* Reply to the command. There is an overloaded version of this
	    * call that accepts a dpp::message so you can send embeds. */
	    bot.log(dpp::ll_debug, event.command.get_issuing_user().username + " " + action);

	    if (action == "add_to_list") {
		bot.log(dpp::ll_debug, "yo");
		dpp::interaction_modal_response modal("my_modal", "Please complete the form...");
		/* Add a text component */
		modal.add_component(
		    dpp::component().
		    set_label("Add a Film to Your List").
		    set_id("field_id").
		    set_type(dpp::cot_text).
		    set_placeholder("enter film title").
		    set_min_length(1).
		    set_max_length(2000).
		    set_text_style(dpp::text_paragraph)
		);

		/* Trigger the dialog box. All dialog boxes are ephemeral */
		event.dialog(modal);
	    }
	    else if (action == "cut_from_list") {
		std::ifstream listInStream { event.command.get_issuing_user().username + "list" };

		if (listInStream.fail()) {
		    dpp::message msg(event.command.channel_id, "You don't have a list!");
		    bot.log(dpp::ll_debug, "failed to open list: " + event.command.get_issuing_user().username + "list"  );
		    event.reply(msg);
		}
		else {
		    dpp::message msg(event.command.channel_id, "Cut a film from your list!");

		    dpp::component selectCutMenu {};
		    selectCutMenu.set_type(dpp::cot_selectmenu)
			.set_placeholder("Pick something")
			.set_id("myselectid");

		    /* reading the list from memory <- 09/08/24 14:53:51 */ 
		    char buff[200] {};
		    JTB::Vec<JTB::Str> listVec {};
		    listInStream.getline(buff, 199);
		    while (listInStream.good()) {
			listVec.push(buff);
			listInStream.getline(buff, 199);
		    }
		    listInStream.close();


		    /* for (int i = 0; i < listVec.size(); i++) { */
			/* selectCutMenu.add_select_option(dpp::select_option(listVec.at(i).c_str(),listVec.at(i).remove(" ").c_str(),"")); */
		    /* } */
		    

		    bot.message_create(dpp::message("bla").set_channel_id(event.command.get_channel().id));
		    /* msg.add_component(dpp::component().add_component(selectCutMenu)); */
		    /* event.reply(msg); */
		    event.reply("test1");
		}
	    }
	}
    });

    /* This event handles form submission for the modal dialog we create above */
    bot.on_form_submit([&](const dpp::form_submit_t & event) {


	/* For this simple example we know the first element of the first row ([0][0]) is value type string.
	 * In the real world it may not be safe to make such assumptions! */
	std::string v = std::get<std::string>(event.components[0].components[0].value);

	std::ifstream listInStream { event.command.get_issuing_user().username + "list" };

	if (listInStream.fail()) {
	    bot.log(dpp::ll_debug, "failed to open list: " + event.command.get_issuing_user().username + "list"  );
	    std::ofstream listOutStream { event.command.get_issuing_user().username + "list" };
	    if (listOutStream.fail()) { throw std::runtime_error("couldn't open ofstream"); }
	    listOutStream << v << '\n';
	}
	else {
	    char buff[200] {};
	    JTB::Vec<JTB::Str> listVec {};
	    listInStream.getline(buff, 199);
	    while (listInStream.good()) {
		listVec.push(buff);
		listInStream.getline(buff, 199);
	    }
	    listVec.push(v);
	    listInStream.close();
	    std::ofstream listOutStream { event.command.get_issuing_user().username + "list" };
	    if (listOutStream.fail()) { throw std::runtime_error("couldn't open ofstream"); }
	    listVec.forEach([&listOutStream](JTB::Str s) {
		listOutStream << s << '\n';
	    });
	}


	dpp::message m {};
	m.set_content("You entered: " + v).set_flags(dpp::m_ephemeral);

	/* Emit a reply. Form submission is still an interaction and must generate some form of reply! */
	event.reply(m);
    });

    /* The on_autocomplete event is fired whenever discord needs information to fill in a command options's choices.
	     * You must reply with a REST event within 500ms, so make it snappy! */
    bot.on_autocomplete([&bot](const dpp::autocomplete_t & event) {
	for (auto& opt : event.options) {
	    /* The option which has focused set to true is the one the user is typing in */
	    if (opt.focused) {
		/* In a real world usage of this function you should return values that loosely match
			 * opt.value, which contains what the user has typed so far. The opt.value is a variant
			 * and will contain the type identical to that of the slash command parameter.
			 * Here we can safely know it is string. */
		std::string uservalue = std::get<std::string>(opt.value);

		bot.interaction_response_create(event.command.id, event.command.token, dpp::interaction_response(dpp::ir_autocomplete_reply)
				  .add_autocomplete_choice(dpp::command_option_choice("add", std::string("add_to_list")))
				  .add_autocomplete_choice(dpp::command_option_choice("cut", std::string("cut_from_list")))
				  .add_autocomplete_choice(dpp::command_option_choice("rand", std::string("show_a_random_list_item")))
				  .add_autocomplete_choice(dpp::command_option_choice("show", std::string("show_your_full_list")))
				  );
		bot.log(dpp::ll_debug, "Autocomplete " + opt.name + " with value '" + uservalue + "' in field " + event.name);
		break;
	    }
	}
    });

    bot.start(dpp::st_wait);

    return 0;
}
