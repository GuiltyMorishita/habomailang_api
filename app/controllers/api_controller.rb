class ApiController < ApplicationController
  def sentence_generator

    shop_name = params[:shop_name]
    menu = params[:menu]
    topping = params[:topping]
    price = params[:price]
    noodle_level = params[:noodle_level]
    soup_level = params[:soup_level]
    pork_level = params[:pork_level]

    noodle = Noodle.where(level: noodle_level).sample
    soup = Soup.where(level: soup_level).sample
    pork = Pork.where(level: pork_level).sample

    youbi = %w[日 月 火 水 木 金 土]
    date = Date.today.to_era("%O%E年%m月%d日") + youbi[Date.today.wday] + "曜日"
    sentence = date + "、" + shop_name + "、" + menu + " " + topping + " " + price + "YEN\n"
    sentence += noodle.sentence + "\n"
    sentence += soup.sentence + "\n"
    sentence += pork.sentence + "\n"
    sentence += "完飲。"

    request = { sentence: sentence }
    render :json => request
  end


  private
  def api_params
    params.permit(:shop_name, :menu, :topping, :price, :noodle_level, :soup_level, :pork_level)
  end
end
