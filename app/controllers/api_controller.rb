class ApiController < ApplicationController
  def sentence_generator

    shop_name = params[:shop_name]
    menu = params[:menu]
    price = params[:price]

    noodle = Noodle.where(level: 1).limit(1)
    soup = Soup.where(level: 1).limit(1)
    pork = Pork.where(level: 1).limit(1)

    youbi = %w[日 月 火 水 木 金 土]
    date = Date.today.to_era("%O%E年%m月%d日") + youbi[Date.today.wday] + "曜日"
    sentence = date + "、" + shop_name + "、" + menu + " " + price + "YEN\n"
    sentence += noodle.first.sentence + "\n"
    sentence += soup.first.sentence + "\n"
    sentence += pork.first.sentence

    render :json => sentence
  end


  private
  def api_params
    params.permit(:shop_name, :menu, :topping, :price, :noodle_level, :soup_level, :pork_level)
  end
end
