class CreatePorks < ActiveRecord::Migration[5.0]
  def change
    create_table :porks do |t|
      t.integer :level, null: false, default: 3
      t.string :sentence, null: false

      t.timestamps
    end
  end
end
