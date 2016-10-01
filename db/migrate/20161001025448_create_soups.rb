class CreateSoups < ActiveRecord::Migration[5.0]
  def change
    create_table :soups do |t|
      t.integer :level, null: false, default: 3
      t.string :sentence, null: false

      t.timestamps
    end
  end
end
